document.addEventListener('DOMContentLoaded', async () => {
  const input = document.getElementById('apiBaseUrl');
  const saveBtn = document.getElementById('save');
  const savedEl = document.getElementById('saved');

  const { apiBaseUrl } = await chrome.storage.local.get('apiBaseUrl');
  input.value = apiBaseUrl || 'http://localhost:8000';

  saveBtn.addEventListener('click', async () => {
    let url = (input.value || '').trim().replace(/\/+$/, '');
    if (!url) url = 'http://localhost:8000';
    await chrome.storage.local.set({ apiBaseUrl: url });
    savedEl.style.display = 'block';
    savedEl.textContent = 'Saved. Reload TCGplayer tabs and retry if needed.';
    setTimeout(() => { savedEl.style.display = 'none'; }, 3000);
  });
});
