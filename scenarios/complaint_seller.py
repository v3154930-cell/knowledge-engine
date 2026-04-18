from typing import Optional, List
from datetime import datetime
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_SELLER_TYPE = "ask_seller_type"
    ASK_SELLER_NAME = "ask_seller_name"
    ASK_SELLER_INN = "ask_seller_inn"
    ASK_SELLER_PHONE = "ask_seller_phone"
    ASK_SELLER_EMAIL = "ask_seller_email"
    ASK_SELLER_ADDRESS = "ask_seller_address"
    ASK_PLATFORM = "ask_platform"
    ASK_VIOLATION_TYPE = "ask_violation_type"
    ASK_VIOLATION_DATE = "ask_violation_date"
    ASK_CONTRACT_NUMBER = "ask_contract_number"
    ASK_DAMAGE_AMOUNT = "ask_damage_amount"
    ASK_DESCRIPTION = "ask_description"
    ASK_SUPPORT_CONTACTED = "ask_support_contacted"
    ASK_TICKET_NUMBER = "ask_ticket_number"
    ASK_MARKETPLACE_RESPONSE = "ask_marketplace_response"
    ASK_DEMANDS = "ask_demands"
    ASK_EVIDENCE = "ask_evidence"
    ASK_DATE = "ask_date"
    DONE = "done"

SELLER_TYPES = ["ИП", "ООО", "Самозанятый"]

PLATFORMS = ["Ozon", "Wildberries", "Яндекс Маркет"]

VIOLATION_TYPES = [
    "Блокировка карточек товара",
    "Удержание денег за утерянный/испорченный товар",
    "Необоснованный штраф",
    "Ложная жалоба на контрафакт",
    "Одностороннее расторжение договора",
    "Завышенные/скрытые комиссии",
    "Другое"
]

EVIDENCE_CHOICES = [
    "Скриншоты переписки с поддержкой",
    "Скриншоты уведомлений о штрафах/блокировках",
    "Договор/оферта",
    "Акты приёма-передачи товара",
    "Фото повреждённого товара",
    "Выписка по счёту"
]


class ComplaintSellerScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return "Выберите тип заявителя: ИП, ООО или Самозанятый"
        elif self.state == Step.ASK_SELLER_TYPE:
            return "Введите наименование организации или ФИО:"
        elif self.state == Step.ASK_SELLER_NAME:
            return "Введите ИНН (для ИП/ООО) или ОГРНИП (для ИП):"
        elif self.state == Step.ASK_SELLER_INN:
            return "Введите телефон для связи:"
        elif self.state == Step.ASK_SELLER_PHONE:
            return "Введите email:"
        elif self.state == Step.ASK_SELLER_EMAIL:
            return "Введите адрес (юридический или фактический):"
        elif self.state == Step.ASK_SELLER_ADDRESS:
            return "Выберите маркетплейс: Ozon, Wildberries или Яндекс Маркет"
        elif self.state == Step.ASK_PLATFORM:
            choices_text = "\n".join([f"{i+1}. {v}" for i, v in enumerate(VIOLATION_TYPES)])
            return f"Выберите тип нарушения:\n{choices_text}"
        elif self.state == Step.ASK_VIOLATION_TYPE:
            return "Введите дату нарушения (ДД.ММ.ГГГГ):"
        elif self.state == Step.ASK_VIOLATION_DATE:
            return "Введите номер договора или оферты (если есть, иначе пропустить):"
        elif self.state == Step.ASK_CONTRACT_NUMBER:
            return "Введите сумму ущерба в рублях (если есть, иначе пропустить):"
        elif self.state == Step.ASK_DAMAGE_AMOUNT:
            return "Подробно опишите ситуацию (что произошло, когда, какие действия предпринимались):"
        elif self.state == Step.ASK_DESCRIPTION:
            return "Обращались ли вы в поддержку маркетплейса? (да/нет)"
        elif self.state == Step.ASK_SUPPORT_CONTACTED:
            return "Введите номер тикета (если есть, иначе пропустить):"
        elif self.state == Step.ASK_TICKET_NUMBER:
            return "Какой ответ вы получили от маркетплейса? (если есть, иначе пропустить):"
        elif self.state == Step.ASK_MARKETPLACE_RESPONSE:
            return "Сформулируйте ваши требования к маркетплейсу:"
        elif self.state == Step.ASK_DEMANDS:
            choices_text = "\n".join([f"{i+1}. {e}" for i, e in enumerate(EVIDENCE_CHOICES)])
            return f"Какие доказательства вы прикладываете? (можно выбрать несколько, например: 1,3,5 или 1 3 5)\nВведите номера через запятую или пробел, либо 'пропустить':\n\n{choices_text}"
        return None
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        if self.state == Step.START:
            self.state = Step.ASK_SELLER_TYPE
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_TYPE:
            if not answer:
                return "Выберите тип заявителя:"
            self.data['seller_type'] = answer
            self.state = Step.ASK_SELLER_NAME
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_NAME:
            if not answer:
                return "Введите наименование или ФИО:"
            self.data['seller_name'] = answer
            self.state = Step.ASK_SELLER_INN
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_INN:
            self.data['seller_inn'] = answer if answer else 'не указан'
            self.state = Step.ASK_SELLER_PHONE
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_PHONE:
            self.data['seller_phone'] = answer if answer else 'не указан'
            self.state = Step.ASK_SELLER_EMAIL
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_EMAIL:
            self.data['seller_email'] = answer if answer else 'не указан'
            self.state = Step.ASK_SELLER_ADDRESS
            return self.get_next_question()
        
        elif self.state == Step.ASK_SELLER_ADDRESS:
            self.data['seller_address'] = answer if answer else 'не указан'
            self.state = Step.ASK_PLATFORM
            return self.get_next_question()
        
        elif self.state == Step.ASK_PLATFORM:
            if not answer:
                return "Выберите маркетплейс:"
            self.data['platform'] = answer
            self.state = Step.ASK_VIOLATION_TYPE
            return self.get_next_question()
        
        elif self.state == Step.ASK_VIOLATION_TYPE:
            if not answer:
                return "Выберите тип нарушения:"
            nums = answer.replace(',', ' ').split()
            selected = []
            for num in nums:
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(VIOLATION_TYPES):
                        selected.append(VIOLATION_TYPES[idx])
                except ValueError:
                    pass
            if selected:
                self.data['violation_type'] = ', '.join(selected)
            else:
                self.data['violation_type'] = answer
            self.state = Step.ASK_VIOLATION_DATE
            return self.get_next_question()
        
        elif self.state == Step.ASK_VIOLATION_DATE:
            self.data['violation_date'] = answer if answer else 'не указана'
            self.state = Step.ASK_CONTRACT_NUMBER
            return self.get_next_question()
        
        elif self.state == Step.ASK_CONTRACT_NUMBER:
            self.data['contract_number'] = answer if answer.lower() not in ['пропустить', 'skip', ''] else 'не указан'
            self.state = Step.ASK_DAMAGE_AMOUNT
            return self.get_next_question()
        
        elif self.state == Step.ASK_DAMAGE_AMOUNT:
            if answer.lower() in ['пропустить', 'skip', '']:
                self.data['damage_amount'] = 'не указана'
            else:
                try:
                    amount = int(float(answer.replace(',', '.')))
                    self.data['damage_amount'] = f"{amount:,}".replace(',', ' ')
                except ValueError:
                    self.data['damage_amount'] = answer
            self.state = Step.ASK_DESCRIPTION
            return self.get_next_question()
        
        elif self.state == Step.ASK_DESCRIPTION:
            if not answer:
                return "Опишите ситуацию:"
            self.data['description'] = answer
            self.state = Step.ASK_SUPPORT_CONTACTED
            return self.get_next_question()
        
        elif self.state == Step.ASK_SUPPORT_CONTACTED:
            answer_lower = answer.lower()
            if 'да' in answer_lower:
                self.data['support_contacted'] = 'Да'
            else:
                self.data['support_contacted'] = 'Нет'
                self.data['ticket_number'] = 'не обращался'
                self.data['marketplace_response'] = 'ответ не получен'
            self.state = Step.ASK_TICKET_NUMBER
            return self.get_next_question()
        
        elif self.state == Step.ASK_TICKET_NUMBER:
            if answer.lower() in ['пропустить', 'skip', '']:
                self.data['ticket_number'] = 'не указан'
            else:
                self.data['ticket_number'] = answer
            self.state = Step.ASK_MARKETPLACE_RESPONSE
            return self.get_next_question()
        
        elif self.state == Step.ASK_MARKETPLACE_RESPONSE:
            if answer.lower() in ['пропустить', 'skip', '']:
                self.data['marketplace_response'] = 'ответ не получен'
            else:
                self.data['marketplace_response'] = answer
            self.state = Step.ASK_DEMANDS
            return self.get_next_question()
        
        elif self.state == Step.ASK_DEMANDS:
            if not answer:
                return "Сформулируйте требования:"
            self.data['demands'] = answer
            self.state = Step.ASK_EVIDENCE
            return self.get_next_question()
        
        elif self.state == Step.ASK_EVIDENCE:
            if answer.lower() in ['пропустить', 'skip', '']:
                self.data['evidence'] = []
            else:
                selected = []
                nums = answer.replace(',', ' ').split()
                for num in nums:
                    try:
                        idx = int(num) - 1
                        if 0 <= idx < len(EVIDENCE_CHOICES):
                            selected.append(EVIDENCE_CHOICES[idx])
                    except ValueError:
                        pass
                self.data['evidence'] = selected
            
            self.data['current_date'] = datetime.now().strftime("%d.%m.%Y")
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        platform = self.data.get('platform', '')
        if platform.lower() in ['ozon', 'озон']:
            platform_name = 'ООО "Озон"'
            platform_address = '123112, г. Москва, Пресненская наб., д. 10, стр. 1'
        elif platform.lower() in ['wildberries', 'вб', 'wb']:
            platform_name = 'ООО "Вайлдберриз"'
            platform_address = '123001, г. Москва, ул. Садовая-Триумфальная, д. 4-10'
        elif platform.lower() in ['яндекс маркет', 'яндекс']:
            platform_name = 'ООО "Яндекс"'
            platform_address = '119021, г. Москва, ул. Льва Толстого, д. 16'
        else:
            platform_name = platform
            platform_address = 'адрес не указан'
        
        seller_type = self.data.get('seller_type', '')
        
        document = f"""ЖАЛОБА / ПРЕТЕНЗИЯ ПРОДАВЦА

{self.data.get('current_date', '')}

От: {seller_type} "{self.data.get('seller_name', '')}"
ИНН/ОГРНИП: {self.data.get('seller_inn', '')}
Адрес: {self.data.get('seller_address', '')}
Телефон: {self.data.get('seller_phone', '')}
Email: {self.data.get('seller_email', '')}

Кому: {platform_name}
{platform_address}

ЖАЛОБА на действия маркетплейса {platform}

Я, {seller_type} "{self.data.get('seller_name', '')}", являюсь продавцом (селлером) на платформе {platform} и заключил(а) с ней договор (оферту).

Договор (оферта) №: {self.data.get('contract_number', '')}
Дата нарушения: {self.data.get('violation_date', '')}

ОПИСАНИЕ НАРУШЕНИЯ:
Тип нарушения: {self.data.get('violation_type', '')}

{self.data.get('description', '')}

СУММА УЩЕРБА: {self.data.get('damage_amount', '')} руб.

ПРЕДПРИНЯТЫЕ ДЕЙСТВИЯ:
Обращение в поддержку: {self.data.get('support_contacted', '')}
Номер тикета: {self.data.get('ticket_number', '')}

Ответ маркетплейса:
{self.data.get('marketplace_response', '')}

ТРЕБОВАНИЯ:
{self.data.get('demands', '')}

"""
        
        evidence = self.data.get('evidence', [])
        if evidence:
            evidence_list = "\n".join([f"{i+1}. {e}" for i, e in enumerate(evidence, 1)])
            document += f"""ПРИЛОЖЕНИЯ (доказательства):
{evidence_list}

"""
        
        document += f"""ПРАВОВОЕ ОБОСНОВАНИЕ:

Действия маркетплейса нарушают положения заключённого договора (оферты), а также могут противоречить:
- Гражданскому кодексу РФ (ст. 309-310 о надлежащем исполнении обязательств)
- Федеральному закону № 135-ФЗ "О защите конкуренции" (запрет на злоупотребление доминирующим положением)
- Федеральному закону № 115-ФЗ "О противодействии легализации" (при необоснованном блокировании средств)

Прошу рассмотреть настоящую жалобу в течение 10 рабочих дней и удовлетворить мои требования в добровольном порядке.

В случае отказа в удовлетворении требований или неполучения ответа я буду вынужден(а) обратиться:
- в Федеральную антимонопольную службу (ФАС)
- в суд с требованием о защите прав и возмещении ущерба
- в прокуратуру

_________________________
{self.data.get('seller_name', '')}
{self.data.get('seller_type', '')}

---
ДИСКЛЕЙМЕР: Информация носит справочный характер. Для сложных споров рекомендуется обратиться к квалифицированному юристу.
"""
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value