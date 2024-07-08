from typing import List

class LLModelList:
    ZH_TW_L3_8B = "chinese_tw_Llama"
    LLAMA3_8B = "llama3:8b"
    LLAVA = "llava"
    
    @staticmethod
    def get_model_list() -> List[str]:
        attributes = [attr for attr in dir(LLModelList) if not attr.startswith("__") and not callable(getattr(LLModelList, attr))]
        return [getattr(LLModelList, attr) for attr in attributes]
