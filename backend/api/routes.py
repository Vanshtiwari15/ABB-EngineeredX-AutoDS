"""All `/api/*` HTTP endpoints."""

from __future__ import annotations

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    UploadFile,
    status,
)

from backend.agents import (
    DataCleanerAgent,
    EvaluatorAgent,
    ModelSelectorAgent,
    ProblemDetectorAgent,
    ReportGeneratorAgent,
)
from backend.api.dependencies import (
    data_cleaner_dep,
    evaluator_dep,
    model_selector_dep,
    prediction_service_dep,
    problem_detector_dep,
    registry_dep,
    report_dep,
    session_dep,
    training_service_dep,
)
from backend.core.config import get_settings
from backend.core.constants import JobState, ModelName, TaskType
from backend.core.exceptions import (
    JobNotFoundError,
    SessionNotReadyError,
)
from backend.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    EvaluateResponse,
    HealthResponse,
    JobModelStatus,
    JobStatusResponse,
    ModelCandidate,
    ModelEvaluation,
    PredictionRecord,
    PredictRequest,
    PredictResponse,
    PrepareRequest,
    PrepareResponse,
    ReportRequest,
    ReportResponse,
    ResetResponse,
    SelectModelsRequest,
    SelectModelsResponse,
    SessionResponse,
    TrainRequest,
    TrainResponse,
    UploadResponse,
)
from backend.services.model_registry import ModelRegistry
from backend.services.pipeline_service import build_preprocessing
from backend.services.prediction_service import PredictionService
from backend.services.session_service import (
    EvaluationInfo,
    PreparationInfo,
    SessionService,
    TaskInfo,
)
from backend.services.training_service import (
    TrainingJobInputs,
    TrainingService,
    get_train_results,
)
from backend.utils.io_utils import read_csv_bytes
from backend.utils.logger import get_correlation_id, get_logger
from backend.utils.validators import validate_upload

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["autods"])


# Health
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    s = get_settings()
    return HealthResponse(status="ok", app=s.app_name, version=s.app_version)


# Upload
@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload(
    file: UploadFile = File(...),
    session: SessionService = Depends(session_dep),
) -> UploadResponse:
    data = await file.read()
    validate_upload(file.filename or "upload.csv", len(data))
    df = read_csv_bytes(data, filename=file.filename or "upload.csv")
    with session.lock:
        s = session.get()
        s.filename = file.filename
        s.df = df
        s.df_clean = None
        s.task = None
        s.preparation = None
        s.selected_models = []
        s.trained_models = {}
        s.evaluation = None
        s.best_model = None
        s.last_job_id = None
    logger.info("Uploaded '%s' shape=%s", file.filename, df.shape)
    return UploadResponse(
        filename=file.filename or "upload.csv",
        n_rows=int(df.shape[0]),
        n_cols=int(df.shape[1]),
        columns=list(df.columns),
        dtypes={c: str(t) for c, t in df.dtypes.items()},
        preview=df.head(5).fillna("").to_dict(orient="records"),
    )


# Analyze
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    body: AnalyzeRequest,
    session: SessionService = Depends(session_dep),
    detector: ProblemDetectorAgent = Depends(problem_detector_dep),
) -> AnalyzeResponse:
    s = session.get()
    if s.df is None:
        raise SessionNotReadyError("No dataset uploaded. POST /api/upload first.")
    inference, profile = detector.detect(s.df, target=body.target, hint=body.task_hint)
    with session.lock:
        s.task = TaskInfo(
            task_type=inference.task_type,
            confidence=inference.confidence,
            reasoning=list(inference.reasoning),
            target=inference.target,
            feature_columns=list(inference.feature_columns),
            text_column=inference.text_column,
            datetime_column=inference.datetime_column,
            profile=profile,
        )
    return AnalyzeResponse(
        task_type=inference.task_type,
        confidence=inference.confidence,
        reasoning=list(inference.reasoning),
        target=inference.target,
        feature_columns=list(inference.feature_columns),
        text_column=inference.text_column,
        datetime_column=inference.datetime_column,
        profile=profile,
    )



# Prepare
@router.post("/prepare", response_model=PrepareResponse)
def prepare(
    body: PrepareRequest,
    session: SessionService = Depends(session_dep),
    cleaner: DataCleanerAgent = Depends(data_cleaner_dep),
) -> PrepareResponse:
    s = session.get()
    if s.df is None:
        raise SessionNotReadyError("No dataset uploaded.")
    if s.task is None:
        raise SessionNotReadyError("Task not detected. POST /api/analyze first.")

    cleaned, _report = cleaner.clean(
        s.df,
        drop_duplicates=body.drop_duplicates,
        target=s.task.target,
        text_column=s.task.text_column,
    )
    plan = build_preprocessing(
        cleaned,
        task_type=s.task.task_type,
        target=s.task.target,
        text_column=s.task.text_column,
        datetime_column=s.task.datetime_column,
        impute_strategy_numeric=body.impute_strategy_numeric,
        impute_strategy_categorical=body.impute_strategy_categorical,
        scale_numeric=body.scale_numeric,
    )
    with session.lock:
        s.df_clean = cleaned
        s.preparation = PreparationInfo(
            pipeline=plan.pipeline,
            steps=list(plan.steps),
            numeric_features=list(plan.numeric_features),
            categorical_features=list(plan.categorical_features),
            text_feature=plan.text_feature,
            n_rows_in=int(s.df.shape[0]),
            n_rows_out=int(cleaned.shape[0]),
            n_features_out=len(plan.feature_names_out),
            feature_names_out=list(plan.feature_names_out),
        )
    return PrepareResponse(
        steps=plan.steps,
        numeric_features=plan.numeric_features,
        categorical_features=plan.categorical_features,
        text_feature=plan.text_feature,
        n_rows_in=int(s.df.shape[0]),
        n_rows_out=int(cleaned.shape[0]),
        n_features_out=len(plan.feature_names_out),
    )



# Select Models
@router.post("/select-models", response_model=SelectModelsResponse)
def select_models(
    body: SelectModelsRequest,
    session: SessionService = Depends(session_dep),
    selector: ModelSelectorAgent = Depends(model_selector_dep),
) -> SelectModelsResponse:
    s = session.get()
    if s.task is None:
        raise SessionNotReadyError("Task not detected. POST /api/analyze first.")
    candidates = selector.select(s.task.task_type, overrides=body.overrides)
    with session.lock:
        s.selected_models = [c.name for c in candidates]
    return SelectModelsResponse(
        task_type=s.task.task_type,
        candidates=[
            ModelCandidate(
                name=c.name,
                library=c.library,
                description=c.description,
                hyperparameters=c.hyperparameters,
            )
            for c in candidates
        ],
    )


# Train
@router.post(
    "/train",
    response_model=TrainResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def train(
    body: TrainRequest,
    background: BackgroundTasks,
    session: SessionService = Depends(session_dep),
    trainer: TrainingService = Depends(training_service_dep),
) -> TrainResponse:
    s = session.get()
    if s.df_clean is None or s.preparation is None:
        raise SessionNotReadyError(
            "Data not prepared. POST /api/prepare before training."
        )
    if s.task is None:
        raise SessionNotReadyError("Task not detected.")
    if not s.selected_models:
        raise SessionNotReadyError(
            "No models selected. POST /api/select-models first."
        )

    settings = get_settings()
    job = session.create_job([m.value for m in s.selected_models])
    inputs = TrainingJobInputs(
        task=s.task,
        preparation=s.preparation,
        df=s.df_clean.copy(),
        selected_models=list(s.selected_models),
        test_size=body.test_size or settings.test_size,
        random_seed=body.random_seed or settings.random_seed,
    )
    correlation_id = get_correlation_id()
    background.add_task(trainer.run_job, job.job_id, inputs, correlation_id)
    return TrainResponse(job_id=job.job_id, state=JobState.PENDING)


@router.get("/train/status/{job_id}", response_model=JobStatusResponse)
def train_status(
    job_id: str,
    session: SessionService = Depends(session_dep),
) -> JobStatusResponse:
    rec = session.get_job(job_id)
    if rec is None:
        raise JobNotFoundError(f"Job '{job_id}' not found.")
    return JobStatusResponse(
        job_id=rec.job_id,
        state=rec.state,
        progress=rec.progress,
        started_at=rec.started_at,
        finished_at=rec.finished_at,
        models=[
            JobModelStatus(
                name=m.name,
                state=m.state,
                error=m.error,
                duration_seconds=m.duration_seconds,
            )
            for m in rec.models
        ],
        error=rec.error,
    )


# Evaluate
@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(
    session: SessionService = Depends(session_dep),
    evaluator: EvaluatorAgent = Depends(evaluator_dep),
) -> EvaluateResponse:
    s = session.get()
    if s.task is None:
        raise SessionNotReadyError("Task not detected.")
    train_results = get_train_results(session)
    if not train_results:
        raise SessionNotReadyError("No trained models. Run /api/train first.")
    eval_result = evaluator.evaluate(s.task.task_type, train_results)
    with session.lock:
        s.evaluation = EvaluationInfo(
            primary_metric=eval_result.primary_metric,
            higher_is_better=eval_result.higher_is_better,
            rankings=list(eval_result.rankings),
            best_model=eval_result.best_model,
            evaluations={k: dict(v) for k, v in eval_result.evaluations.items()},
        )
        s.best_model = eval_result.best_model
    return EvaluateResponse(
        task_type=s.task.task_type,
        primary_metric=eval_result.primary_metric,
        higher_is_better=eval_result.higher_is_better,
        rankings=list(eval_result.rankings),
        best_model=eval_result.best_model,
        evaluations=[
            ModelEvaluation(name=k, metrics=v)
            for k, v in eval_result.evaluations.items()
        ],
    )


# Predict
@router.post("/predict", response_model=PredictResponse)
def predict(
    body: PredictRequest,
    predictor: PredictionService = Depends(prediction_service_dep),
) -> PredictResponse:
    chosen, records = predictor.predict(body.rows, body.model_name)
    return PredictResponse(
        model_name=chosen,
        n=len(records),
        predictions=[PredictionRecord(**r) for r in records],
    )


# Report
@router.post("/report", response_model=ReportResponse)
def report(
    body: ReportRequest,
    session: SessionService = Depends(session_dep),
    reporter: ReportGeneratorAgent = Depends(report_dep),
) -> ReportResponse:
    s = session.get()
    if s.df is None:
        raise SessionNotReadyError("No dataset in session.")
    artifacts = reporter.generate(s, title=body.title)
    return ReportResponse(
        json_path=str(artifacts.json_path),
        markdown_path=str(artifacts.markdown_path),
        summary=artifacts.summary,
    )


# Session / Reset
@router.get("/session", response_model=SessionResponse)
def session_view(
    session: SessionService = Depends(session_dep),
) -> SessionResponse:
    s = session.get()
    if s.df is None:
        return SessionResponse(has_dataset=False)

    dataset = {
        "filename": s.filename,
        "n_rows": int(s.df.shape[0]),
        "n_cols": int(s.df.shape[1]),
        "columns": list(s.df.columns),
    }
    task = None
    if s.task is not None:
        task = AnalyzeResponse(
            task_type=s.task.task_type,
            confidence=s.task.confidence,
            reasoning=list(s.task.reasoning),
            target=s.task.target,
            feature_columns=list(s.task.feature_columns),
            text_column=s.task.text_column,
            datetime_column=s.task.datetime_column,
            profile=s.task.profile,
        )
    preparation = None
    if s.preparation is not None:
        preparation = PrepareResponse(
            steps=list(s.preparation.steps),
            numeric_features=list(s.preparation.numeric_features),
            categorical_features=list(s.preparation.categorical_features),
            text_feature=s.preparation.text_feature,
            n_rows_in=s.preparation.n_rows_in,
            n_rows_out=s.preparation.n_rows_out,
            n_features_out=s.preparation.n_features_out,
        )
    last_job = None
    if s.last_job_id is not None:
        rec = session.get_job(s.last_job_id)
        if rec is not None:
            last_job = JobStatusResponse(
                job_id=rec.job_id,
                state=rec.state,
                progress=rec.progress,
                started_at=rec.started_at,
                finished_at=rec.finished_at,
                models=[
                    JobModelStatus(
                        name=m.name,
                        state=m.state,
                        error=m.error,
                        duration_seconds=m.duration_seconds,
                    )
                    for m in rec.models
                ],
                error=rec.error,
            )
    evaluation = None
    if s.evaluation is not None:
        evaluation = EvaluateResponse(
            task_type=s.task.task_type if s.task else TaskType.CLASSIFICATION,
            primary_metric=s.evaluation.primary_metric,
            higher_is_better=s.evaluation.higher_is_better,
            rankings=list(s.evaluation.rankings),
            best_model=s.evaluation.best_model,
            evaluations=[
                ModelEvaluation(name=k, metrics=v)
                for k, v in s.evaluation.evaluations.items()
            ],
        )
    return SessionResponse(
        has_dataset=True,
        dataset=dataset,
        task=task,
        preparation=preparation,
        selected_models=list(s.selected_models),
        trained_models=list(s.trained_models),
        last_job=last_job,
        evaluation=evaluation,
        best_model=s.best_model,
    )


@router.post("/reset", response_model=ResetResponse)
def reset(
    session: SessionService = Depends(session_dep),
    registry: ModelRegistry = Depends(registry_dep),
) -> ResetResponse:
    removed = registry.remove_all()
    session.reset()
    return ResetResponse(cleared=True, removed_files=removed)


# Re-export ModelName so generated OpenAPI schema documents the enum.
_ = ModelName