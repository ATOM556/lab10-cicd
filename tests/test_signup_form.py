"""Автотесты пользовательского интерфейса формы записи (лабораторная работа 10).

Тесты проверяют поведение формы: успешную отправку, клиентскую валидацию,
отображение выбранного тарифа и переключатель показа пароля.
"""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

TIMEOUT = 10


def _fill(page, fullname="Иванов Иван", email="ivanov@example.com",
          phone="+375 29 123-45-67", password="Secret123"):
    page.find_element(By.ID, "fullname").send_keys(fullname)
    page.find_element(By.ID, "email").send_keys(email)
    page.find_element(By.ID, "phone").send_keys(phone)
    page.find_element(By.ID, "password").send_keys(password)


def test_page_loads_with_form(page):
    """Страница открывается: заголовок, форма и поля ввода на месте."""
    assert page.title == "BaseOfGamers — запись в компьютерный клуб"

    form = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "signup-form")))
    assert form.is_displayed()

    for field_id in ("fullname", "email", "phone", "plan", "password"):
        assert page.find_element(By.ID, field_id).is_displayed()


def test_submit_with_valid_data_shows_success_message(page):
    """Позитивный сценарий: корректные данные создают запись."""
    _fill(page)
    page.find_element(By.ID, "submit-button").click()

    success = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "success-message")))
    details = page.find_element(By.ID, "success-details").text

    assert "Запись создана" in success.text
    assert "Иванов Иван" in details

    records = page.find_elements(By.CSS_SELECTOR, ".record-item")
    assert len(records) == 1
    assert "ivanov@example.com" in records[0].text


def test_empty_name_shows_validation_error(page):
    """Негативный сценарий: пустое имя приводит к сообщению об ошибке."""
    _fill(page, fullname="")
    page.find_element(By.ID, "submit-button").click()

    error = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "fullname-error")))

    assert "Укажите фамилию и имя" in error.text
    assert not page.find_element(By.ID, "success-message").is_displayed()


def test_invalid_email_shows_validation_error(page):
    """Негативный сценарий: некорректный адрес почты отклоняется."""
    _fill(page, email="не-почта")
    page.find_element(By.ID, "submit-button").click()

    error = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "email-error")))

    assert "Некорректный адрес" in error.text
    assert not page.find_element(By.ID, "success-message").is_displayed()


def test_short_password_shows_validation_error(page):
    """Негативный сценарий: короткий пароль отклоняется."""
    _fill(page, password="123")
    page.find_element(By.ID, "submit-button").click()

    error = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "password-error")))

    assert "не менее 6 символов" in error.text


def test_selected_plan_is_shown_in_summary(page):
    """Выбранный тариф отражается в итоговом сообщении и в списке записей."""
    plan = page.find_element(By.ID, "plan")
    Select(plan).select_by_value("6")

    _fill(page)
    page.find_element(By.ID, "submit-button").click()

    details = WebDriverWait(page, TIMEOUT).until(
        EC.visibility_of_element_located((By.ID, "success-details"))).text

    assert "6 часов" in details

    record = page.find_element(By.CSS_SELECTOR, ".record-item")
    assert record.get_attribute("data-plan") == "6"
    assert "6 часов" in record.text


def test_password_toggle_switches_input_type(page):
    """Переключатель показа пароля меняет тип поля ввода."""
    password = page.find_element(By.ID, "password")
    assert password.get_attribute("type") == "password"

    page.find_element(By.ID, "toggle-password").click()

    assert page.find_element(By.ID, "password").get_attribute("type") == "text"
    assert page.find_element(By.ID, "toggle-password").text == "Скрыть"
