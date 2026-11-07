"""Настройка автотестов пользовательского интерфейса (лабораторная работа 10).

Локально поднимается статический HTTP-сервер с проверяемым веб-приложением.
В CI/CD (GitHub Actions) тесты запускаются против того же приложения,
а при наличии переменной BASE_URL — против уже опубликованной версии.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

APP_DIR = Path(__file__).resolve().parents[1] / "app"
EXTERNAL_BASE_URL = os.environ.get("BASE_URL")
HEADED = os.environ.get("HEADED", "").lower() in ("1", "true", "yes")


def _free_port() -> int:
    """Подбирает свободный TCP-порт для локального сервера."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _QuietHandler(SimpleHTTPRequestHandler):
    """Обработчик запросов без вывода в консоль."""

    def log_message(self, fmt, *args):  # noqa: D102 - подавляем шум сервера
        pass


@pytest.fixture(scope="session")
def base_url():
    """Адрес проверяемого приложения: внешний BASE_URL либо локальный сервер."""
    if EXTERNAL_BASE_URL:
        yield EXTERNAL_BASE_URL.rstrip("/")
        return

    port = _free_port()
    handler = partial(_QuietHandler, directory=str(APP_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()


def _chrome_available() -> bool:
    if os.environ.get("CI"):
        return True
    if shutil.which("google-chrome") or shutil.which("google-chrome-stable"):
        return True
    return Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe").exists()


@pytest.fixture(scope="session")
def browser(base_url: str):
    """Запускает браузер (по умолчанию в headless-режиме)."""
    browser_name = os.environ.get("BROWSER", "auto")
    if browser_name == "auto":
        browser_name = "chrome" if _chrome_available() else "edge"

    if browser_name == "chrome":
        options = ChromeOptions()
        if not HEADED:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
    else:
        options = EdgeOptions()
        if not HEADED:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        driver = webdriver.Edge(options=options)

    driver.get(base_url)
    time.sleep(0.5)

    yield driver

    driver.quit()


@pytest.fixture()
def page(browser, request):
    """Открытая страница приложения; при падении теста сохраняется снимок экрана."""
    yield browser

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        shots_dir = Path(__file__).resolve().parents[1] / "reports" / "screenshots"
        shots_dir.mkdir(parents=True, exist_ok=True)
        browser.save_screenshot(str(shots_dir / f"{request.node.name}.png"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет результат вызова для обработчика снимков экрана."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def _reset_page(page, base_url):
    """Перед каждым тестом возвращает страницу в исходное состояние."""
    page.get(base_url)
    yield
