from typing import Optional
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_APPLICANT_FIO = "ask_applicant_fio"
    ASK_APPLICANT_PASSPORT = "ask_applicant_passport"
    ASK_APPLICANT_ADDRESS = "ask_applicant_address"
    ASK_VIOLATOR = "ask_violator"
    ASK_VIOLATION = "ask_violation"
    ASK_DEMAND = "ask_demand"
    DONE = "done"

class ComplaintProsecutorScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return "Введите ваше ФИО (полностью):"
        elif self.state == Step.ASK_APPLICANT_FIO:
            return "Введите ваши паспортные данные (серия, номер, кем и когда выдан):"
        elif self.state == Step.ASK_APPLICANT_PASSPORT:
            return "Введите ваш адрес проживания:"
        elif self.state == Step.ASK_APPLICANT_ADDRESS:
            return "Введите наименование нарушителя (организация или ФИО):"
        elif self.state == Step.ASK_VIOLATOR:
            return "Опишите суть нарушения (что произошло, когда, какие законы нарушены):"
        elif self.state == Step.ASK_VIOLATION:
            return "Сформулируйте ваше требование:"
        return None
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        if self.state == Step.START:
            self.state = Step.ASK_APPLICANT_FIO
            return self.get_next_question()
        
        elif self.state == Step.ASK_APPLICANT_FIO:
            if not answer:
                return "Введите ваше ФИО:"
            self.data['applicant_fio'] = answer
            self.state = Step.ASK_APPLICANT_PASSPORT
            return self.get_next_question()
        
        elif self.state == Step.ASK_APPLICANT_PASSPORT:
            if not answer:
                return "Введите паспортные данные:"
            self.data['applicant_passport'] = answer
            self.state = Step.ASK_APPLICANT_ADDRESS
            return self.get_next_question()
        
        elif self.state == Step.ASK_APPLICANT_ADDRESS:
            if not answer:
                return "Введите адрес:"
            self.data['applicant_address'] = answer
            self.state = Step.ASK_VIOLATOR
            return self.get_next_question()
        
        elif self.state == Step.ASK_VIOLATOR:
            if not answer:
                return "Введите наименование нарушителя:"
            self.data['violator'] = answer
            self.state = Step.ASK_VIOLATION
            return self.get_next_question()
        
        elif self.state == Step.ASK_VIOLATION:
            if not answer:
                return "Опишите суть нарушения:"
            self.data['violation'] = answer
            self.state = Step.ASK_DEMAND
            return self.get_next_question()
        
        elif self.state == Step.ASK_DEMAND:
            if not answer:
                return "Сформулируйте требование:"
            self.data['demand'] = answer
            
            from datetime import datetime
            self.data['current_date'] = datetime.now().strftime("%d.%m.%Y")
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        document = f"""ЖАЛОБА В ПРОКУРАТУРУ

{self.data.get('current_date', '')}

Прокуратура г. Москвы
Адрес: 107996, г. Москва, Малый Кисельный пер., д. 5

От: {self.data.get('applicant_fio', '')}
Паспорт: {self.data.get('applicant_passport', '')}
Адрес: {self.data.get('applicant_address', '')}

ЖАЛОБА

Я, {self.data.get('applicant_fio', '')}, обращаюсь в прокуратуру с жалобой на действия (бездействие) нарушителя.

СУТЬ НАРУШЕНИЯ:
{self.data.get('violation', '')}

НАРУШИТЕЛЬ: {self.data.get('violator', '')}

Указанные действия нарушают мои права и законные интересы.

В соответствии со ст. 10 Федерального закона "О прокуратуре Российской Федерации" прокуратура осуществляет надзор за соблюдением прав и свобод человека и гражданина органами государственной власти и местного самоуправления, а также должностными лицами.

ТРЕБОВАНИЕ:
{self.data.get('demand', '')}

Прошу провести проверку изложенных фактов и принять меры прокурорского реагирования.

При необходимости я готов(а) предоставить дополнительные материалы и документы.

_________________________
{self.data.get('applicant_fio', '')}
"""
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value