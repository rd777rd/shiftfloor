/**
 * Progressive-disclosure stepper for the shift-posting form (Design Plan
 * Flow A / Rubric A.3). Pure vanilla JS, no framework — groups the single
 * ShiftForm's fields into steps client-side; the form still submits as one
 * normal POST, so server-side validation in ShiftForm.clean() is the real
 * source of truth (progressive disclosure is a UX layer, not a validation
 * boundary).
 */
document.addEventListener("DOMContentLoaded", function () {
  var stepper = document.querySelector("[data-stepper]");
  if (!stepper) return;

  var steps = Array.prototype.slice.call(stepper.querySelectorAll(".stepper__step"));
  var progressEls = Array.prototype.slice.call(stepper.querySelectorAll(".stepper__progress span"));
  var current = 0;

  function render() {
    steps.forEach(function (step, i) {
      step.classList.toggle("is-active", i === current);
    });
    progressEls.forEach(function (el, i) {
      el.classList.toggle("is-complete", i <= current);
    });
  }

  stepper.addEventListener("click", function (e) {
    if (e.target.matches("[data-step-next]")) {
      e.preventDefault();
      var fields = steps[current].querySelectorAll("input, select, textarea");
      var valid = true;
      fields.forEach(function (f) {
        if (!f.checkValidity()) {
          f.reportValidity();
          valid = false;
        }
      });
      if (!valid) return;
      if (current < steps.length - 1) {
        current += 1;
        render();
      }
    }
    if (e.target.matches("[data-step-back]")) {
      e.preventDefault();
      if (current > 0) {
        current -= 1;
        render();
      }
    }
  });

  render();
});
