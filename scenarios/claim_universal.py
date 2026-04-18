from typing import Optional
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_RECIPIENT = "ask_recipient"
    ASK_ADDRESS = "ask_address"
    ASK_INN = "ask_inn"
    ASK_SENDER_FIO = "ask_sender_fio"
    ASK_SENDER_PASSPORT = "ask_sender_passport"
    ASK_ISSUE = "ask_issue"
    ASK_DEMAND = "ask_demand"
    ASK_DATE = "ask_date"
    DONE = "done"

class ClaimUniversalScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return "Введите наименование получателя претензии (организация или ФИО):"
        elif self.state == Step.ASK_RECIPIENT:
            return "Введите адрес получателя:"
        elif self.state == Step.ASK_ADDRESS:
            return "Введите ИНН получателя (если известен, иначе пропустите):"
        elif self.state == Step.ASK_INN:
            return "Введите ваше ФИО (полностью):"
        elif self.state == Step.ASK_SENDER_FIO:
            return "Введите ваши паспортные данные (серия, номер, кем и когда выдан):"
        elif self.state == Step.ASK_SENDER_PASSPORT:
            return "Опишите суть проблемы (что произошло, когда, какие нарушены права):"
        elif self.state == Step.ASK_ISSUE:
            return "Сформулируйте ваше требование (чего вы хотите добиться):"
        elif self.state == Step.ASK_DEMAND:
            return "Введите дату составления претензии (ДД.ММ.ГГГГ):"
        return None
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        if self.state == Step.START:
            self.state = Step.ASK_RECIPIENT
            return self.get_next_question()
        
        elif self.state == Step.ASK_RECIPIENT:
            if not answer:
                return "Введите наименование получателя:"
            self.data['recipient'] = answer
            self.state = Step.ASK_ADDRESS
            return self.get_next_question()
        
        elif self.state == Step.ASK_ADDRESS:
            if not answer:
                return "Введите адрес получателя:"
            self.data['address'] = answer
            self.state = Step.ASK_INN
            return self.get_next_question()
        
        elif self.state == Step.ASK_INN:
            self.data['inn'] = answer if answer else 'не указан'
            self.state = Step.ASK_SENDER_FIO
            return self.get_next_question()
        
        elif self.state == Step.ASK_SENDER_FIO:
            if not answer:
                return "Введите ваше ФИО:"
            self.data['sender_fio'] = answer
            self.state = Step.ASK_SENDER_PASSPORT
            return self.get_next_question()
        
        elif self.state == Step.ASK_SENDER_PASSPORT:
            if not answer:
                return "Введите паспортные данные:"
            self.data['sender_passport'] = answer
            self.state = Step.ASK_ISSUE
            return self.get_next_question()
        
        elif self.state == Step.ASK_ISSUE:
            if not answer:
                return "Опишите суть проблемы:"
            self.data['issue'] = answer
            self.state = Step.ASK_DEMAND
            return self.get_next_question()
        
        elif self.state == Step.ASK_DEMAND:
            if not answer:
                return "Сформулируйте требование:"
            self.data['demand'] = answer
            self.state = Step.ASK_DATE
            return self.get_next_question()
        
        elif self.state == Step.ASK_DATE:
            if not answer:
                return "Введите дату в формате ДД.ММ.ГГГГ:"
            self.data['date'] = answer
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        document = f"""ПРЕТЕНЗИЯ

{self.data.get('date', '')}

{self.data.get('recipient', '')}
Адрес: {self.data.get('address', '')}
{self.data.get('inn', '')}

От: {self.data.get('sender_fio', '')}
Паспорт: {self.data.get('sender_passport', '')}

ПРЕТЕНЗИЯ

Я, {self.data.get('sender_fio', '')}, являюсь потребителем товаров и услуг.

СУТЬ ПРЕТЕНЗИИ:
{self.data.get('issue', '')}

ТРЕБОВАНИЕ:
{self.data.get('demand', '')}

Прошу рассмотреть настоящую претензию в течение 10 дней с момента её получения и удовлетворить мои требования в добровольном порядке.

В случае отказа в удовлетворении моих требований или неполучения ответа в установленный срок я буду вынужден(а) обратиться в суд за защитой своих прав, а также в соответствующие контролирующие органы.

_________________________
{self.data.get('sender_fio', '')}
"""
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value