from typing import Optional
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_APPLICANT_FIO = "ask_applicant_fio"
    ASK_APPLICANT_PASSPORT = "ask_applicant_passport"
    ASK_BANK = "ask_bank"
    ASK_BIK = "ask_bik"
    ASK_ACCOUNT = "ask_account"
    ASK_BLOCK_DATE = "ask_block_date"
    ASK_VIOLATION_TYPE = "ask_violation_type"
    ASK_AMOUNT = "ask_amount"
    DONE = "done"

class ClaimBankBlockScenario:
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
            return "Введите наименование банка:"
        elif self.state == Step.ASK_BANK:
            return "Введите БИК банка:"
        elif self.state == Step.ASK_BIK:
            return "Введите номер вашего расчётного счёта:"
        elif self.state == Step.ASK_ACCOUNT:
            return "Введите дату блокировки счёта (ДД.ММ.ГГГГ):"
        elif self.state == Step.ASK_BLOCK_DATE:
            return "Укажите тип нарушения (необоснованная блокировка, отказ в проведении операции, требование избыточных документов, другое):"
        elif self.state == Step.ASK_VIOLATION_TYPE:
            return "Введите сумму заблокированных средств в рублях:"
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
            self.state = Step.ASK_BANK
            return self.get_next_question()
        
        elif self.state == Step.ASK_BANK:
            if not answer:
                return "Введите наименование банка:"
            self.data['bank'] = answer
            self.state = Step.ASK_BIK
            return self.get_next_question()
        
        elif self.state == Step.ASK_BIK:
            self.data['bik'] = answer if answer else 'не указан'
            self.state = Step.ASK_ACCOUNT
            return self.get_next_question()
        
        elif self.state == Step.ASK_ACCOUNT:
            if not answer:
                return "Введите номер счёта:"
            self.data['account'] = answer
            self.state = Step.ASK_BLOCK_DATE
            return self.get_next_question()
        
        elif self.state == Step.ASK_BLOCK_DATE:
            if not answer:
                return "Введите дату в формате ДД.ММ.ГГГГ:"
            self.data['block_date'] = answer
            self.state = Step.ASK_VIOLATION_TYPE
            return self.get_next_question()
        
        elif self.state == Step.ASK_VIOLATION_TYPE:
            if not answer:
                return "Укажите тип нарушения:"
            self.data['violation_type'] = answer
            self.state = Step.ASK_AMOUNT
            return self.get_next_question()
        
        elif self.state == Step.ASK_AMOUNT:
            try:
                amount = int(float(answer.replace(',', '.')))
                if amount < 0:
                    return "Сумма не может быть отрицательной. Введите сумму:"
                self.data['amount'] = f"{amount:,}".replace(',', ' ')
            except ValueError:
                return "Пожалуйста, введите число (например: 50000):"
            
            from datetime import datetime
            self.data['current_date'] = datetime.now().strftime("%d.%m.%Y")
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        document = f"""ПРЕТЕНЗИЯ (по ФЗ-115)

{self.data.get('current_date', '')}

{self.data.get('bank', '')}
БИК: {self.data.get('bik', '')}

От: {self.data.get('applicant_fio', '')}
Паспорт: {self.data.get('applicant_passport', '')}
Расчётный счёт: {self.data.get('account', '')}

ПРЕТЕНЗИЯ по факту блокировки счёта на основании ФЗ-115

{self.data.get('current_date', '')} года моёму расчётному счёту № {self.data.get('account', '')} в банке {self.data.get('bank', '')} была заблокирована сумма в размере {self.data.get('amount', '')} руб. на основании Федерального закона № 115-ФЗ "О противодействии легализации (отмыванию) доходов, полученных преступным путём, и финансированию терроризма".

Тип нарушения: {self.data.get('violation_type', '')}

Считаю действия банка незаконными и нарушающими мои права по следующим основаниям:

1. Банк обязан осуществлять идентификацию клиентов в соответствии с требованиями п. 10 ст. 7 ФЗ-115, однако моя личность была идентифицирована при открытии счёта.

2. Банк не вправе безосновательно блокировать операции и счёта клиента. Согласно п. 11 ст. 7 ФЗ-115 основания для отказа в проведении операции должны быть объективными и документально подтверждёнными.

3. Согласно п. 13.1.1 ст. 7 ФЗ-115 банк обязан направлять уведомление клиенту о приостановлении операций, однако надлежащее уведомление мной получено не было.

4. Согласно п. 14 ст. 7 ФЗ-115 клиент вправе обжаловать действия банка.

ТРЕБОВАНИЯ:
1. Разблокировать мой расчётный счёт №{self.data.get('account', '')}
2. Обеспечить беспрепятственное проведение операций по счёту
3. Предоставить письменное обоснование блокировки счёта

Прошу рассмотреть настоящую претензию в течение 10 дней с момента её получения и удовлетворить мои требования в добровольном порядке.

В случае отказа в удовлетворении требований или неполучения ответа я буду вынужден(а) обратиться в ЦБ РФ, прокуратуру и суд.

_________________________
{self.data.get('applicant_fio', '')}
"""
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value