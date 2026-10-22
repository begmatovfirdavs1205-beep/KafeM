document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.main-nav');
  if (toggle && nav) toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  const updateFulfillment = (input) => {
    const address = document.querySelector('.address-field');
    const pickup = input.value === 'pickup' && input.checked;
    if (address) address.hidden = pickup;
    const summary = document.querySelector('.order-summary');
    if (summary && input.checked) {
      const fee = pickup ? 0 : Number(summary.dataset.delivery || 0);
      const subtotal = Number(summary.dataset.subtotal || 0);
      const amount = new Intl.NumberFormat('ru-TJ', { maximumFractionDigits: 2 }).format(subtotal + fee);
      const feeLabel = document.querySelector('.checkout-delivery-fee');
      const totalLabel = document.querySelector('.checkout-total');
      if (feeLabel) feeLabel.textContent = fee === 0 ? 'Бесплатно' : `${new Intl.NumberFormat('ru-TJ', { maximumFractionDigits: 2 }).format(fee)} сомони`;
      if (totalLabel) totalLabel.textContent = `${amount} сомони`;
    }
  };
  document.querySelectorAll('input[name="fulfillment"]').forEach((input) => {
    input.addEventListener('change', () => {
      updateFulfillment(input);
    });
    if (input.checked) updateFulfillment(input);
  });
});
