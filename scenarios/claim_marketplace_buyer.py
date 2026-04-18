from typing import Optional, List
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_MARKETPLACE = "ask_marketplace"
    ASK_ORDER_NUMBER = "ask_order_number"
    ASK_PRODUCT = "ask_product"
    ASK_AMOUNT = "ask_amount"
    ASK_FIO = "ask_fio"
    ASK_PASSPORT = "ask_passport"
    ASK_DATE = "ask_date"
    ASK_REASON = "ask_reason"
    ASK_EVIDENCE = "ask_evidence"
    DONE = "done"

EVIDENCE_CHOICES = [
    "Чек / квитанция об оплате",
    "Скриншоты переписки с продавцом",
    "Фотографии товара (брак, упаковка)",
    "Видеофиксация (распаковка, работа товара)",
    "Скриншот заказа с маркетплейса",
    "Трек-номер отправления",
    "Другое (укажу в тексте)"
]

class ClaimMarketplaceBuyerScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return "Выберите маркетплейс (Ozon, WB или Яндекс):"
        elif self.state == Step.ASK_MARKETPLACE:
            return "Введите номер заказа:"
        elif self.state == Step.ASK_ORDER_NUMBER:
            return "Введите наименование товара:"
        elif self.state == Step.ASK_PRODUCT:
            return "Введите сумму заказа в рублях:"
        elif self.state == Step.ASK_AMOUNT:
            return "Введите ваше ФИО (полностью):"
        elif self.state == Step.ASK_FIO:
            return "Введите паспортные данные (серия, номер, кем и когда выдан):"
        elif self.state == Step.ASK_PASSPORT:
            return "Введите дату, когда должен был быть доставлен товар (ДД.ММ.ГГГГ):"
        elif self.state == Step.ASK_DATE:
            return "Выберите причину претензии: нарушение срока доставки, отмена заказа, некачественный товар, не тот товар, другое"
        elif self.state == Step.ASK_EVIDENCE:
            choices_text = "\n".join([f"{i+1}. {choice}" for i, choice in enumerate(EVIDENCE_CHOICES)])
            return f"Какие доказательства вы прикладываете к претензии? (можно выбрать несколько, например: 1,3,5 или 1 3 5)\nВведите номера через запятую или пробел, либо 'пропустить' для продолжения без приложений:\n\n{choices_text}"
        return None
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        if self.state == Step.START:
            self.state = Step.ASK_MARKETPLACE
            return self.get_next_question()
        
        elif self.state == Step.ASK_MARKETPLACE:
            if not answer:
                return "Выберите маркетплейс (Ozon, WB или Яндекс):"
            self.data['marketplace'] = answer
            self.state = Step.ASK_ORDER_NUMBER
            return self.get_next_question()
        
        elif self.state == Step.ASK_ORDER_NUMBER:
            if not answer:
                return "Введите номер заказа:"
            self.data['order_number'] = answer
            self.state = Step.ASK_PRODUCT
            return self.get_next_question()
        
        elif self.state == Step.ASK_PRODUCT:
            if not answer:
                return "Введите наименование товара:"
            self.data['product'] = answer
            self.state = Step.ASK_AMOUNT
            return self.get_next_question()
        
        elif self.state == Step.ASK_AMOUNT:
            try:
                amount = int(float(answer.replace(',', '.')))
                if amount <= 0:
                    return "Сумма должна быть больше нуля. Введите сумму в рублях:"
                self.data['amount'] = f"{amount:,}".replace(',', ' ')
                self.data['amount_raw'] = amount
            except ValueError:
                return "Пожалуйста, введите число (например: 50000):"
            self.state = Step.ASK_FIO
            return self.get_next_question()
        
        elif self.state == Step.ASK_FIO:
            if not answer:
                return "Введите ваше ФИО полностью:"
            self.data['fio'] = answer
            self.state = Step.ASK_PASSPORT
            return self.get_next_question()
        
        elif self.state == Step.ASK_PASSPORT:
            if not answer:
                return "Введите паспортные данные:"
            self.data['passport'] = answer
            self.state = Step.ASK_DATE
            return self.get_next_question()
        
        elif self.state == Step.ASK_DATE:
            if not answer:
                return "Введите дату в формате ДД.ММ.ГГГГ:"
            self.data['delivery_date'] = answer
            self.state = Step.ASK_REASON
            return self.get_next_question()
        
        elif self.state == Step.ASK_REASON:
            if not answer:
                return "Выберите причину претензии:"
            reason_lower = answer.lower()
            if 'нарушение срока' in reason_lower or 'срок' in reason_lower:
                self.data['reason'] = 'нарушение срока доставки'
                self.data['penalty_days'] = 10
                penalty = int(self.data['amount_raw'] * 0.005 * 10)
                self.data['penalty'] = f"{penalty:,}".replace(',', ' ')
                self.data['penalty_reason'] = 'просрочка доставки (10 дней × 0.5% = 5%)'
            elif 'отмена' in reason_lower:
                self.data['reason'] = 'отмена заказа'
                self.data['penalty_days'] = 10
                penalty = int(self.data['amount_raw'] * 0.005 * 10)
                self.data['penalty'] = f"{penalty:,}".replace(',', ' ')
                self.data['penalty_reason'] = 'отмена заказа продавцом (10 дней × 0.5% = 5%)'
            elif 'некачествен' in reason_lower:
                self.data['reason'] = 'некачественный товар'
                self.data['penalty'] = '0'
            elif 'не тот' in reason_lower:
                self.data['reason'] = 'не тот товар'
                self.data['penalty'] = '0'
            else:
                self.data['reason'] = answer
                self.data['penalty'] = '0'
            
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
            
            from datetime import datetime
            self.data['current_date'] = datetime.now().strftime("%d.%m.%Y")
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        marketplace = self.data.get('marketplace', '')
        if marketplace.lower() == 'ozon':
            recipient = 'ООО "Озон"'
            address = '123112, г. Москва, Пресненская наб., д. 10, стр. 1'
            inn = 'ИНН 7728024512'
        elif marketplace.lower() == 'wb' or marketplace.lower() == 'wildberries':
            recipient = 'ООО "Вайлдберриз"'
            address = '123001, г. Москва, ул. Садовая-Триумфальная, д. 4-10'
            inn = 'ИНН 7704217371'
        elif marketplace.lower() == 'яндекс':
            recipient = 'ООО "Яндекс"'
            address = '119021, г. Москва, ул. Льва Толстого, д. 16'
            inn = 'ИНН 7704148147'
        else:
            recipient = marketplace
            address = 'адрес'
            inn = 'ИНН'
        
        document = f"""ПРЕТЕНЗИЯ

{self.data.get('current_date', '')}

{recipient}
{address}
{inn}

От: {self.data.get('fio', '')}
Паспорт: {self.data.get('passport', '')}

ПРЕТЕНЗИЯ по заказу №{self.data.get('order_number', '')}

Я приобрел(а) на маркетплейсе {marketplace} товар: {self.data.get('product', '')} на сумму {self.data.get('amount', '')} руб.

Номер заказа: {self.data.get('order_number', '')}
Дата предполагаемой доставки: {self.data.get('delivery_date', '')}

Причина претензии: {self.data.get('reason', '')}

"""
        
        if self.data.get('penalty', '0') != '0':
            document += f"""В связи с нарушением моих прав как потребителя, в соответствии со ст. 18, 23.1, 26.1 Закона РФ "О защите прав потребителей", я требую:

1. Вернуть уплаченные деньги в размере {self.data.get('amount', '')} руб.
2. Выплатить неустойку за {self.data.get('penalty_days', '')} дней просрочки в размере {self.data.get('penalty', '')} руб. ({self.data.get('penalty_reason', '')})
3. Общая сумма к возврату: {int(self.data.get('amount_raw', 0)) + int(self.data.get('penalty', '0').replace(' ', ''))} руб.

"""
        else:
            document += f"""В связи с нарушением моих прав как потребителя, в соответствии со ст. 18, 23.1, 26.1 Закона РФ "О защите прав потребителей", я требую:

1. Вернуть уплаченные деньги в размере {self.data.get('amount', '')} руб.
2. Заменить товар на качественный или вернуть деньги

"""
        
        evidence = self.data.get('evidence', [])
        if evidence:
            evidence_list = "\n".join([f"  - {e}" for e in evidence])
            document += f"""Приложение:
{evidence_list}

"""
        
        document += f"""Согласно ст. 18 Закона РФ "О защите прав потребителей" потребитель вправе требовать возврата уплаченных денежных средств.
Согласно ст. 23.1 Закона РФ "О защите прав потребителей" за нарушение сроков доставки продавец уплачивает неустойку в размере 0,5% от цены товара за каждый день просрочки.
Согласно ст. 26.1 Закона РФ "О защите прав потребителей" (дистанционный способ продажи) потретель вправе отказаться от товара в любое время до его передачи.

Прошу рассмотреть претензию в течение 10 дней с момента получения и возвратить денежные средства.

В случае неудовлетворения требований я буду вынужден(а) обратиться в суд с требованием о защите прав потребителя, а также в Роспотребнадзор.

_________________________
{self.data.get('fio', '')}
"""
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value