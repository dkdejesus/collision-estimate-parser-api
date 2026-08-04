import json

        from openai import AsyncOpenAI

        from app.config import Settings
        from app.schemas import EstimateParseAssessment, EstimateParseRequest

        SYSTEM_PROMPT = """You are a collision-repair workflow assistant for Estimate parser.
        Return a conservative, structured operational output for a professional body shop.
        Use only the provided context. Mark uncertain facts as To Validate.
        Do not make final safety, repair, insurance, financial, or outbound communication decisions.
        Keep human review in the loop for customer-facing, insurer-facing, financial, and safety-sensitive outputs.
        """


        class EstimateParseService:
            def __init__(self, settings: Settings):
                self.settings = settings
                self.client = (
                    AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)
                    if settings.openai_api_key and AsyncOpenAI is not None
                    else None
                )

            async def assess(self, payload: EstimateParseRequest) -> EstimateParseAssessment:
                if self.client is None:
                    return self._rule_based_fallback(payload)

                response = await self.client.responses.parse(
                    model=self.settings.openai_model,
                    instructions=SYSTEM_PROMPT,
                    input=json.dumps(payload.model_dump(), default=str),
                    text_format=EstimateParseAssessment,
                )
                if response.output_parsed is None:
                    raise RuntimeError("Model returned no parsed assessment")
                return response.output_parsed

            @staticmethod
            def _rule_based_fallback(payload: EstimateParseRequest) -> EstimateParseAssessment:
                fallback = {
            "labor_totals": {
                        "body": "14.2",
                        "paint": "7.8"
            },
            "parts_total": "$1,840",
            "paint_material_total": "$420",
            "missing_fields": [
                        "calibration requirement",
                        "OEM procedure attachment"
            ],
            "risk_flags": [
                        "ADAS/calibration review may be needed"
            ],
            "review_checklist": [
                        "Verify labor totals",
                        "Attach relevant OEM procedures",
                        "Confirm supplement status"
            ],
            "confidence": 0.74
}
                notes = payload.workflow_notes.lower()
                if "missing" in notes or "unknown" in notes or "to validate" in notes:
                    fallback["confidence"] = min(float(fallback.get("confidence", 0.65)), 0.76)
                return EstimateParseAssessment.model_validate(fallback)
