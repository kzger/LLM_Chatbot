from typing import List

class LLModelList:
    ZH_TW_L3_8B = "chinese_tw_Llama"
    LLAMA3_8B = "llama3:latest"
    LLAVA = "llava"
    PROMPT = "impactframes/llama3_ifai_sd_prompt_mkr_q4km:latest"
    
    @staticmethod
    def get_model_list() -> List[str]:
        attributes = [attr for attr in dir(LLModelList) if not attr.startswith("__") and not callable(getattr(LLModelList, attr))]
        return [getattr(LLModelList, attr) for attr in attributes]
