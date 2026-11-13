from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_report_generator
from app.schemas.workflow_schema import PromptWorkflowRequest, WorkflowRequest, WorkflowResponse
from app.services.report_generator import ReportGenerator
from app.services.prompt_intake import brand_from_prompt
from app.services.workflow import WorkflowAgentError, run_complete_workflow

router = APIRouter(prefix="/api/v1/workflow", tags=["Four-agent workflow"])


@router.post("/run", response_model=WorkflowResponse, summary="Run Persons 1-4 with one bounded critic revision")
async def run_workflow(request: WorkflowRequest, generator: ReportGenerator = Depends(get_report_generator)) -> WorkflowResponse:
    try:
        return await run_complete_workflow(request, generator)
    except WorkflowAgentError as exc:
        raise HTTPException(status_code=502, detail={"agent": exc.agent, "message": str(exc)}) from exc
    except ValueError as exc:
        # Missing credentials and malformed provider responses are configuration
        # errors, not an apparently successful campaign.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Four-agent workflow failed: {exc}") from exc


@router.post("/run-from-prompt", response_model=WorkflowResponse, summary="Run the complete campaign from one natural-language brand prompt")
async def run_workflow_from_prompt(request: PromptWorkflowRequest, generator: ReportGenerator = Depends(get_report_generator)) -> WorkflowResponse:
    try:
        brand = brand_from_prompt(request.prompt)
        return await run_complete_workflow(
            WorkflowRequest(
                brand=brand,
                generate_image=request.generate_poster,
                generate_poster=request.generate_poster,
                max_revisions=request.max_revisions,
            ),
            generator,
        )
    except WorkflowAgentError as exc:
        raise HTTPException(status_code=502, detail={"agent": exc.agent, "message": str(exc)}) from exc
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=f"Campaign intake failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Four-agent workflow failed: {exc}") from exc
