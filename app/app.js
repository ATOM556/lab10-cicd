/* Логика формы записи в компьютерный клуб. */
(function () {
  "use strict";

  var form = document.getElementById("signup-form");
  var successBox = document.getElementById("success-message");
  var successDetails = document.getElementById("success-details");
  var recordsList = document.getElementById("records-list");
  var toggleButton = document.getElementById("toggle-password");
  var passwordField = document.getElementById("password");

  var PLAN_LABELS = {
    "1": "1 час — 15 BYN",
    "3": "3 часа — 40 BYN",
    "6": "6 часов — 76 BYN",
    "12": "12 часов — 144 BYN"
  };

  function showError(id, message) {
    var box = document.getElementById(id + "-error");
    box.textContent = message;
    box.hidden = false;
    document.getElementById(id).classList.add("invalid");
  }

  function clearError(id) {
    var box = document.getElementById(id + "-error");
    box.textContent = "";
    box.hidden = true;
    document.getElementById(id).classList.remove("invalid");
  }

  function validate(values) {
    var errors = {};

    if (!values.fullname.trim()) {
      errors.fullname = "Укажите фамилию и имя";
    } else if (values.fullname.trim().length < 3) {
      errors.fullname = "Имя должно содержать не менее 3 символов";
    }

    if (!values.email.trim()) {
      errors.email = "Укажите электронную почту";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(values.email.trim())) {
      errors.email = "Некорректный адрес электронной почты";
    }

    if (!values.phone.trim()) {
      errors.phone = "Укажите номер телефона";
    } else if (!/^\+?[\d\s\-()]{7,20}$/.test(values.phone.trim())) {
      errors.phone = "Некорректный номер телефона";
    }

    if (!values.password) {
      errors.password = "Укажите пароль";
    } else if (values.password.length < 6) {
      errors.password = "Пароль должен содержать не менее 6 символов";
    }

    return errors;
  }

  function renderRecords(records) {
    recordsList.innerHTML = "";
    if (!records.length) {
      var empty = document.createElement("li");
      empty.className = "empty";
      empty.textContent = "Записей пока нет";
      recordsList.appendChild(empty);
      return;
    }
    records.forEach(function (record) {
      var item = document.createElement("li");
      item.className = "record-item";
      item.setAttribute("data-plan", record.plan);
      item.textContent = record.fullname + " — " + record.email + " — " + PLAN_LABELS[record.plan];
      recordsList.appendChild(item);
    });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var values = {
      fullname: document.getElementById("fullname").value,
      email: document.getElementById("email").value,
      phone: document.getElementById("phone").value,
      plan: document.getElementById("plan").value,
      password: document.getElementById("password").value
    };

    ["fullname", "email", "phone", "password"].forEach(clearError);

    var errors = validate(values);
    var errorIds = Object.keys(errors);
    if (errorIds.length) {
      errorIds.forEach(function (field) {
        showError(field, errors[field]);
      });
      document.getElementById(errorIds[0]).focus();
      successBox.hidden = true;
      return;
    }

    var plan = PLAN_LABELS[values.plan];
    successDetails.textContent = values.fullname.trim() + ", тариф: " + plan;
    successBox.hidden = false;

    var records = Array.prototype.slice
      .call(recordsList.querySelectorAll(".record-item"))
      .map(function (node) {
        return {
          fullname: node.textContent.split(" — ")[0],
          email: node.textContent.split(" — ")[1],
          plan: node.getAttribute("data-plan")
        };
      });
    records.unshift({
      fullname: values.fullname.trim(),
      email: values.email.trim(),
      plan: values.plan
    });
    renderRecords(records);

    form.reset();
  });

  toggleButton.addEventListener("click", function () {
    var isHidden = passwordField.type === "password";
    passwordField.type = isHidden ? "text" : "password";
    toggleButton.textContent = isHidden ? "Скрыть" : "Показать";
    toggleButton.setAttribute("aria-label", isHidden ? "Скрыть пароль" : "Показать пароль");
  });
})();
