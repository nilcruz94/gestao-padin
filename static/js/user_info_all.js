/* user_info_all.js
   ✅ Versão corrigida para:
   - edição inline no prontuário do servidor
   - formulário de dados pessoais separado do formulário de e-mail
   - modal de progresso já existente no HTML (#progressModal)
   - ativar/inativar via AJAX
   - alterar e-mail
   - relatório individual e relatório completo
   - seleção manual no modal de relatório
*/

function toggleDetails(headerEl) {
  if (!headerEl) return;
  const details = headerEl.nextElementSibling;
  if (!details) return;

  const isOpen = details.style.display === 'block';
  details.style.display = isOpen ? 'none' : 'block';
  headerEl.classList.toggle('open', !isOpen);
  headerEl.setAttribute('aria-expanded', String(!isOpen));
}

function expandAll() {
  document.querySelectorAll('.user-header').forEach((header) => {
    const details = header.nextElementSibling;
    if (details && details.style.display !== 'block') {
      details.style.display = 'block';
      header.classList.add('open');
      header.setAttribute('aria-expanded', 'true');
    }
  });
}

function collapseAll() {
  document.querySelectorAll('.user-header').forEach((header) => {
    const details = header.nextElementSibling;
    if (details && details.style.display !== 'none') {
      details.style.display = 'none';
      header.classList.remove('open');
      header.setAttribute('aria-expanded', 'false');
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  const expandAllBtn = document.getElementById('expandAllBtn');
  const collapseAllBtn = document.getElementById('collapseAllBtn');

  const alertBox = document.getElementById('statusAlert');

  const modalBackdrop = document.getElementById('confirmModal');
  const modalTitle = document.getElementById('confirmModalTitle');
  const modalMessage = document.getElementById('confirmModalMessage');
  const modalBtnCancel = document.getElementById('confirmModalCancel');
  const modalBtnConfirm = document.getElementById('confirmModalConfirm');

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
  let currentAction = null;
  let activeAbortController = null;

  function showAlert(message, type = 'success') {
    if (!alertBox) return;

    const icon =
      type === 'success'
        ? 'fa-circle-check'
        : type === 'error'
          ? 'fa-triangle-exclamation'
          : 'fa-circle-info';

    alertBox.innerHTML = `
      <div class="alert-toast ${type}">
        <div class="icon">
          <i class="fa-solid ${icon}"></i>
        </div>
        <div>${message}</div>
      </div>
    `;

    setTimeout(() => {
      if (alertBox) alertBox.innerHTML = '';
    }, 4500);
  }

  // ==========================================================
  // MODAL DE PROGRESSO (usa o HTML existente)
  // ==========================================================
  const progressModal = document.getElementById('progressModal');
  const pgTitle = document.getElementById('pgTitle');
  const pgMsg = document.getElementById('pgMsg');
  const pgFill = document.getElementById('pgFill');
  const pgStatus = document.getElementById('pgStatus');
  const pgPct = document.getElementById('pgPct');
  const pgMeta = document.getElementById('pgMeta');
  const pgMetaText = document.getElementById('pgMetaText');
  const pgCancelBtn = document.getElementById('pgCancelBtn');
  const pgOkBtn = document.getElementById('pgOkBtn');
  const pgCloseBtn = document.getElementById('pgCloseBtn');

  let progressTimer = null;
  let progressValue = 0;
  let progressCap = 88;
  let progressIsActive = false;

  function showProgressModal() {
    if (!progressModal) return;
    progressModal.classList.add('show');
    progressModal.setAttribute('aria-hidden', 'false');
  }

  function hideProgressModal() {
    if (!progressModal) return;
    progressModal.classList.remove('show');
    progressModal.setAttribute('aria-hidden', 'true');
  }

  function resetProgressModal() {
    progressValue = 0;

    if (pgFill) {
      pgFill.classList.add('indeterminate');
      pgFill.classList.remove('determinate');
      pgFill.style.width = '0%';
    }

    if (pgPct) pgPct.textContent = '—';
    if (pgStatus) pgStatus.textContent = 'Gerando no servidor…';
    if (pgMeta) pgMeta.style.display = 'none';
    if (pgMetaText) pgMetaText.textContent = '';
    if (pgOkBtn) pgOkBtn.style.display = 'none';
    if (pgCancelBtn) pgCancelBtn.style.display = '';
  }

  function setProgressTitle(title, sub) {
    if (pgTitle && title) pgTitle.textContent = String(title);
    if (pgMsg && sub) pgMsg.textContent = String(sub);
  }

  function setProgress(pct, statusText) {
    const v = Math.max(0, Math.min(100, Number(pct || 0)));
    progressValue = v;

    if (pgFill) {
      pgFill.classList.remove('indeterminate');
      pgFill.classList.add('determinate');
      pgFill.style.width = `${v}%`;
    }

    if (pgPct) pgPct.textContent = `${Math.round(v)}%`;
    if (pgStatus && statusText) pgStatus.textContent = String(statusText);
  }

  function showProgressMeta(text) {
    if (pgMeta) pgMeta.style.display = 'flex';
    if (pgMetaText) pgMetaText.textContent = String(text || '');
  }

  function startProgress({ title, sub, startPct = 4, cap = 88 }) {
    progressCap = Math.max(60, Math.min(95, cap || 88));
    progressIsActive = true;

    resetProgressModal();
    showProgressModal();
    setProgressTitle(title || 'Gerando relatório…', sub || 'Aguarde enquanto o sistema prepara o arquivo.');
    setProgress(startPct, 'Iniciando…');

    if (progressTimer) clearInterval(progressTimer);
    progressTimer = setInterval(() => {
      if (!progressIsActive) return;

      const distance = progressCap - progressValue;
      if (distance <= 0) return;

      const step = Math.max(0.25, Math.min(1.8, distance / 18));
      setProgress(progressValue + step, pgStatus?.textContent || 'Processando…');
    }, 280);
  }

  function finishProgressSuccess(msg, metaText) {
    progressIsActive = false;
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = null;

    setProgress(100, msg || 'Concluído.');
    if (metaText) showProgressMeta(metaText);

    if (pgCancelBtn) pgCancelBtn.style.display = 'none';
    if (pgOkBtn) pgOkBtn.style.display = '';

    setTimeout(() => {
      hideProgressModal();
      resetProgressModal();
    }, 900);
  }

  function finishProgressError(msg) {
    progressIsActive = false;
    if (progressTimer) clearInterval(progressTimer);
    progressTimer = null;

    setProgress(Math.max(8, Math.min(95, progressValue)), msg || 'Falha.');

    if (pgCancelBtn) pgCancelBtn.style.display = 'none';
    if (pgOkBtn) pgOkBtn.style.display = '';

    setTimeout(() => {
      hideProgressModal();
      resetProgressModal();
    }, 1300);
  }

  if (pgCancelBtn) {
    pgCancelBtn.addEventListener('click', () => {
      if (activeAbortController) activeAbortController.abort();
    });
  }

  if (pgOkBtn) {
    pgOkBtn.addEventListener('click', () => {
      hideProgressModal();
      resetProgressModal();
    });
  }

  if (pgCloseBtn) {
    pgCloseBtn.addEventListener('click', () => {
      hideProgressModal();
    });
  }

  if (progressModal) {
    progressModal.addEventListener('click', (event) => {
      if (event.target === progressModal) {
        hideProgressModal();
      }
    });
  }

  // ==========================================================
  // ALTERAR E-MAIL
  // ==========================================================
  function openEmailForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    document.querySelectorAll('.email-edit-form.open').forEach((openForm) => {
      if (openForm.id !== formId) {
        openForm.classList.remove('open');
        const input = openForm.querySelector('input[type="email"]');
        if (input) input.value = '';
      }
    });

    form.classList.add('open');
    const input = form.querySelector('input[type="email"]');
    if (input) input.focus();
  }

  function closeEmailForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.classList.remove('open');
    const input = form.querySelector('input[type="email"]');
    if (input) input.value = '';
  }

  document.querySelectorAll('.email-toggle-btn').forEach((btn) => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const targetId = btn.getAttribute('data-target');
      if (!targetId) return;

      const form = document.getElementById(targetId);
      if (!form) return;

      const isOpen = form.classList.contains('open');
      if (isOpen) closeEmailForm(targetId);
      else openEmailForm(targetId);
    });
  });

  document.querySelectorAll('.email-cancel-btn').forEach((btn) => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const targetId = btn.getAttribute('data-target');
      if (targetId) closeEmailForm(targetId);
    });
  });

  document.querySelectorAll('.email-edit-form').forEach((form) => {
    form.addEventListener('click', (e) => e.stopPropagation());

    form.addEventListener('submit', function () {
      const submitBtn = form.querySelector('button[type="submit"]');
      const cancelBtn = form.querySelector('.email-cancel-btn');

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i> Atualizando...';
      }

      if (cancelBtn) cancelBtn.disabled = true;
    });
  });

  // ==========================================================
  // EDIÇÃO INLINE DO PRONTUÁRIO
  // ==========================================================
  const inlineForms = Array.from(document.querySelectorAll('.inline-user-edit-form'));

  function getLinkedDataForm(inlineContainer) {
    if (!inlineContainer) return null;
    const formId = inlineContainer.getAttribute('data-form-id');
    if (!formId) return null;
    return document.getElementById(formId);
  }

  function exitInlineEditMode(form, restoreOriginals = false) {
    if (!form) return;

    const editBtn = form.querySelector('.inline-edit-toggle-btn');
    const saveBtn = form.querySelector('.inline-save-btn');
    const cancelBtn = form.querySelector('.inline-cancel-btn');
    const inputs = Array.from(form.querySelectorAll('.inline-edit-input'));

    if (restoreOriginals) {
      inputs.forEach((input) => {
        if (input.dataset.originalValue !== undefined) {
          input.value = input.dataset.originalValue;
        }
      });
    }

    form.classList.remove('is-editing');

    if (editBtn) editBtn.hidden = false;
    if (saveBtn) {
      saveBtn.hidden = true;
      saveBtn.disabled = false;
      saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Salvar';
    }
    if (cancelBtn) {
      cancelBtn.hidden = true;
      cancelBtn.disabled = false;
    }
  }

  function enterInlineEditMode(form) {
    if (!form) return;

    inlineForms.forEach((other) => {
      if (other !== form) exitInlineEditMode(other, true);
    });

    const editBtn = form.querySelector('.inline-edit-toggle-btn');
    const saveBtn = form.querySelector('.inline-save-btn');
    const cancelBtn = form.querySelector('.inline-cancel-btn');
    const inputs = Array.from(form.querySelectorAll('.inline-edit-input'));

    inputs.forEach((input) => {
      input.dataset.originalValue = input.value;
    });

    form.classList.add('is-editing');

    if (editBtn) editBtn.hidden = true;
    if (saveBtn) saveBtn.hidden = false;
    if (cancelBtn) cancelBtn.hidden = false;

    const firstInput = inputs.find((el) => !el.disabled && el.type !== 'hidden');
    if (firstInput) firstInput.focus();
  }

  inlineForms.forEach((form) => {
    form.addEventListener('click', (e) => e.stopPropagation());

    const editBtn = form.querySelector('.inline-edit-toggle-btn');
    const cancelBtn = form.querySelector('.inline-cancel-btn');
    const linkedForm = getLinkedDataForm(form);

    if (editBtn) {
      editBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        enterInlineEditMode(form);
      });
    }

    if (cancelBtn) {
      cancelBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        exitInlineEditMode(form, true);
      });
    }

    if (linkedForm) {
      linkedForm.addEventListener('submit', function () {
        const saveBtn = form.querySelector('.inline-save-btn');
        const cancelBtnInside = form.querySelector('.inline-cancel-btn');

        if (saveBtn) {
          saveBtn.disabled = true;
          saveBtn.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i> Salvando...';
        }

        if (cancelBtnInside) cancelBtnInside.disabled = true;
      });
    }
  });

  // ==========================================================
  // ABRIR / FECHAR CARDS
  // ==========================================================
  document.querySelectorAll('.user-header').forEach((header) => {
    header.addEventListener('click', function (event) {
      if (
        event.target.closest('.metric') ||
        event.target.closest('.toggle-ativo-btn') ||
        event.target.closest('.email-toggle-btn') ||
        event.target.closest('.report-single-btn') ||
        event.target.closest('.inline-edit-toolbar') ||
        event.target.closest('.inline-edit-input') ||
        event.target.closest('.email-edit-form') ||
        event.target.closest('form') ||
        event.target.closest('button') ||
        event.target.closest('a') ||
        event.target.closest('input') ||
        event.target.closest('select') ||
        event.target.closest('textarea') ||
        event.target.closest('label')
      ) {
        return;
      }

      toggleDetails(header);
    });

    header.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        if (event.target.closest('input, button, a, select, textarea, label, form')) return;
        event.preventDefault();
        toggleDetails(header);
      }
    });
  });

  // ==========================================================
  // ABRIR DETALHES TRE/BH
  // ==========================================================
  document.querySelectorAll('.metric.metric-clickable').forEach((metric) => {
    metric.addEventListener('click', function (event) {
      event.stopPropagation();

      const card = metric.closest('.user-card');
      if (!card) return;

      const type = metric.getAttribute('data-metric');
      if (type === 'tre') {
        const treBox = card.querySelector('.tre-details');
        if (treBox) treBox.classList.toggle('open');
      } else if (type === 'bh') {
        const bhBox = card.querySelector('.bh-details');
        if (bhBox) bhBox.classList.toggle('open');
      }
    });
  });

  if (expandAllBtn) expandAllBtn.addEventListener('click', expandAll);
  if (collapseAllBtn) collapseAllBtn.addEventListener('click', collapseAll);

  // ==========================================================
  // MODAL ATIVAR / INATIVAR
  // ==========================================================
  function closeConfirmModal() {
    if (!modalBackdrop) return;
    modalBackdrop.classList.remove('show');
    modalBackdrop.setAttribute('aria-hidden', 'true');
    if (modalBtnConfirm) modalBtnConfirm.disabled = false;
  }

  document.querySelectorAll('.toggle-ativo-btn').forEach((btn) => {
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();

      const userId = btn.getAttribute('data-user-id');
      const userNome = btn.getAttribute('data-user-nome') || 'Usuário';
      const url = btn.getAttribute('data-url');
      const ativo = btn.getAttribute('data-ativo') === '1';

      currentAction = { userId, userNome, url, ativo };

      if (modalTitle && modalMessage && modalBtnConfirm) {
        if (ativo) {
          modalTitle.textContent = 'Marcar como inativo';
          modalMessage.innerHTML = `Tem certeza que deseja marcar <strong>${userNome}</strong> como <strong>inativo</strong>?`;
          modalBtnConfirm.textContent = 'Sim, inativar';
          modalBtnConfirm.classList.remove('confirm-ativar');
        } else {
          modalTitle.textContent = 'Marcar como ativo';
          modalMessage.innerHTML = `Tem certeza que deseja marcar <strong>${userNome}</strong> como <strong>ativo</strong>?`;
          modalBtnConfirm.textContent = 'Sim, ativar';
          modalBtnConfirm.classList.add('confirm-ativar');
        }
      }

      if (modalBackdrop) {
        modalBackdrop.classList.add('show');
        modalBackdrop.setAttribute('aria-hidden', 'false');
      }
    });
  });

  if (modalBtnConfirm) {
    modalBtnConfirm.addEventListener('click', function () {
      if (!currentAction) return;
      modalBtnConfirm.disabled = true;

      const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
      };

      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
        headers['X-CSRF-Token'] = csrfToken;
      }

      fetch(currentAction.url, {
        method: 'POST',
        headers,
        credentials: 'same-origin',
        body: JSON.stringify({})
      })
        .then(async (resp) => {
          if (!resp.ok) {
            const text = await resp.text().catch(() => '');
            if (resp.status === 400 && /csrf|token/i.test(text)) {
              throw new Error('Falha de segurança (CSRF). Recarregue a página e tente novamente.');
            }
            throw new Error('Erro ao comunicar com o servidor (HTTP ' + resp.status + ').');
          }

          let data;
          try {
            data = await resp.json();
          } catch (e) {
            throw new Error('Resposta inválida do servidor.');
          }

          if (!data || !data.success) {
            throw new Error((data && data.error) || 'Erro ao alterar status.');
          }

          const novoAtivo = !!data.ativo;
          const userId = currentAction.userId;
          const userNome = currentAction.userNome;

          document.querySelectorAll(`.status-pill[data-user-id="${userId}"]`).forEach((pill) => {
            pill.classList.toggle('status-ativo', novoAtivo);
            pill.classList.toggle('status-inativo', !novoAtivo);
            pill.innerHTML = `
              <i class="fa-solid fa-circle${novoAtivo ? '-check' : '-minus'}"></i>
              ${novoAtivo ? 'Ativo' : 'Inativo'}
            `;
          });

          document.querySelectorAll(`.toggle-ativo-btn[data-user-id="${userId}"]`).forEach((button) => {
            button.setAttribute('data-ativo', novoAtivo ? '1' : '0');
            button.classList.toggle('ativar', !novoAtivo);
            button.classList.toggle('inativar', novoAtivo);

            const txt = (button.textContent || '').toLowerCase();
            const isDetailsButton = txt.includes('marcar como');

            if (isDetailsButton) {
              button.innerHTML = novoAtivo
                ? '<i class="fa-solid fa-user-slash"></i> Marcar como inativo'
                : '<i class="fa-solid fa-user-check"></i> Marcar como ativo';
            } else {
              button.innerHTML = novoAtivo
                ? '<i class="fa-solid fa-user-slash"></i> Inativar'
                : '<i class="fa-solid fa-user-check"></i> Ativar';
            }
          });

          closeConfirmModal();
          currentAction = null;

          showAlert(
            novoAtivo
              ? `Usuário "${userNome}" marcado como ativo.`
              : `Usuário "${userNome}" marcado como inativo.`,
            'success'
          );
        })
        .catch((err) => {
          closeConfirmModal();
          currentAction = null;
          showAlert(err?.message || 'Não foi possível comunicar com o servidor.', 'error');
        });
    });
  }

  if (modalBtnCancel) {
    modalBtnCancel.addEventListener('click', function () {
      closeConfirmModal();
      currentAction = null;
    });
  }

  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', function (event) {
      if (event.target === modalBackdrop) {
        closeConfirmModal();
        currentAction = null;
      }
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modalBackdrop?.classList.contains('show')) {
      closeConfirmModal();
      currentAction = null;
    }
  });

  // ==========================================================
  // HELPERS DOWNLOAD
  // ==========================================================
  function parseFilenameFromContentDisposition(cd) {
    if (!cd) return null;
    const m = cd.match(/filename\*?=(?:UTF-8''|")?([^";\n]+)"?/i);
    if (!m) return null;
    try {
      return decodeURIComponent(m[1].trim());
    } catch {
      return m[1].trim();
    }
  }

  async function readBlobWithProgress(res, onProgress) {
    const total = Number(res.headers.get('Content-Length') || 0);

    if (!res.body || !res.body.getReader) {
      const blob = await res.blob();
      if (onProgress) onProgress(1, total || blob.size || 0);
      return blob;
    }

    const reader = res.body.getReader();
    const chunks = [];
    let received = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      received += value.byteLength;
      if (onProgress) onProgress(received, total);
    }

    return new Blob(chunks, {
      type: res.headers.get('Content-Type') || 'application/octet-stream'
    });
  }

  async function downloadFile(url, fallbackName, opts = {}) {
    const { signal, onStage, onDownloadProgress, mode } = opts;

    const u = new URL(url, window.location.origin);
    u.searchParams.set('_ts', String(Date.now()));

    if (onStage) onStage('Conectando ao servidor…');

    const res = await fetch(u.toString(), {
      method: 'GET',
      credentials: 'same-origin',
      signal
    });

    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      throw new Error(txt || ('Falha ao gerar relatório (HTTP ' + res.status + ').'));
    }

    if (onStage) onStage('Recebendo arquivo…');

    const cd = res.headers.get('Content-Disposition') || '';
    const filename = parseFilenameFromContentDisposition(cd) || fallbackName || 'arquivo';

    const blob = await readBlobWithProgress(res, onDownloadProgress);
    const blobUrl = window.URL.createObjectURL(blob);

    if (mode === 'open') {
      window.open(blobUrl, '_blank', 'noopener,noreferrer');
      setTimeout(() => window.URL.revokeObjectURL(blobUrl), 60000);
      return;
    }

    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 1500);
  }

  // ==========================================================
  // RELATÓRIO INDIVIDUAL
  // ==========================================================
  document.querySelectorAll('.report-single-btn').forEach((a) => {
    a.addEventListener('click', async (e) => {
      if (e.ctrlKey || e.metaKey || e.button === 1) return;

      const uid = a.getAttribute('data-user-id');
      const nome = a.getAttribute('data-user-nome') || 'servidor';
      const url = a.getAttribute('href');

      if (e.altKey || e.shiftKey) {
        e.preventDefault();
        e.stopPropagation();

        if (uid) {
          openReportModal({ preselectUserId: String(uid), preselectUserName: nome });
        } else {
          openReportModal();
        }
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      if (!url) return;

      const original = a.innerHTML;
      a.style.pointerEvents = 'none';
      a.style.opacity = '0.75';
      a.innerHTML = '<i class="fa-solid fa-rotate fa-spin"></i> Gerando…';

      activeAbortController = new AbortController();

      startProgress({
        title: 'Gerando relatório individual…',
        sub: `Servidor: ${nome}`,
        startPct: 6,
        cap: 86
      });

      try {
        showAlert('Gerando relatório de ' + nome + '…', 'success');

        await downloadFile(url, 'relatorio_servidor.pdf', {
          signal: activeAbortController.signal,
          mode: 'download',
          onStage: (stage) => {
            setProgress(Math.max(progressValue, 10), stage);
          },
          onDownloadProgress: (received, total) => {
            if (total > 0) {
              const pct = Math.min(99, Math.max(0, (received / total) * 100));
              const mapped = 88 + (pct * 0.11);
              setProgress(Math.max(progressValue, mapped), 'Baixando arquivo…');
            } else {
              setProgress(Math.max(progressValue, 88), 'Baixando arquivo…');
            }
          }
        });

        finishProgressSuccess('Relatório pronto.', 'Arquivo baixado com sucesso.');
        showAlert('Relatório do servidor gerado.', 'success');
      } catch (err) {
        if (err && (err.name === 'AbortError' || /aborted/i.test(String(err.message || '')))) {
          finishProgressError('Cancelado pelo usuário.');
          showAlert('Geração cancelada.', 'error');
        } else {
          finishProgressError(err?.message || 'Não foi possível gerar.');
          showAlert(err?.message || 'Não foi possível gerar o relatório do servidor.', 'error');
        }
      } finally {
        activeAbortController = null;
        a.innerHTML = original;
        a.style.pointerEvents = '';
        a.style.opacity = '';
      }
    });
  });

  // ==========================================================
  // MODAL RELATÓRIO COMPLETO
  // ==========================================================
  const reportModal = document.getElementById('reportModal');
  const reportCloseBtn = document.getElementById('reportCloseBtn');
  const reportCancelBtn = document.getElementById('reportCancelBtn');
  const reportGenerateBtn = document.getElementById('reportGenerateBtn');
  const reportEndpointEl = document.getElementById('reportEndpoint');

  const dtIniEl = document.getElementById('dtIni');
  const dtFimEl = document.getElementById('dtFim');

  const typesAllBtn = document.getElementById('typesAllBtn');
  const typesNoneBtn = document.getElementById('typesNoneBtn');

  const manualWrap = document.getElementById('manualWrap');
  const manualList = document.getElementById('manualList');
  const manualSelectedCountEl = document.getElementById('manualSelectedCount');
  const manualResultsCountEl = document.getElementById('manualResultsCount');
  const manualPageLabelEl = document.getElementById('manualPageLabel');
  const userSearchInput = document.getElementById('userSearchInput');
  const userSearchStatus = document.getElementById('userSearchStatus');
  const manualPrevBtn = document.getElementById('manualPrevBtn');
  const manualNextBtn = document.getElementById('manualNextBtn');
  const manualClearBtn = document.getElementById('manualClearBtn');
  const manualSelectPageBtn = document.getElementById('manualSelectPageBtn');
  const manualSelectAllResultsBtn = document.getElementById('manualSelectAllResultsBtn');
  const chipRow = document.getElementById('chipRow');

  const btnReport = document.getElementById('btnReport');

  const pvUsersEl = document.getElementById('pvUsers');
  const pvRegsEl = document.getElementById('pvRegs');
  const pvDetailEl = document.getElementById('pvDetail');
  const pvRefreshBtn = document.getElementById('pvRefreshBtn');

  const rememberPrefsCb = document.getElementById('rememberPrefsCb');
  const zipHint = document.getElementById('zipHint');
  const actionOpenItem = document.getElementById('actionOpenItem');

  const presets = Array.from(document.querySelectorAll('.preset-btn'));
  const PREF_KEY = 'padin_report_prefs_v1';

  const state = {
    manual: {
      page: 1,
      per_page: 40,
      total: 0,
      has_more: false,
      items: [],
      selected: new Map(),
      last_q: '',
      last_status: 'ativos'
    },
    preset: ''
  };

  function getReportBaseUrl() {
    return reportEndpointEl?.getAttribute('data-report-url') || '';
  }

  function getCountUrl() {
    return reportEndpointEl?.getAttribute('data-count-url') || '';
  }

  function getSearchUrl() {
    return reportEndpointEl?.getAttribute('data-users-search-url') || '';
  }

  function getStatsUrl() {
    return reportEndpointEl?.getAttribute('data-stats-url') || '';
  }

  function getCurrentQ() {
    return reportEndpointEl?.getAttribute('data-q') || '';
  }

  function getCurrentStatus() {
    return reportEndpointEl?.getAttribute('data-status') || 'ativos';
  }

  function hasCurrentFilter() {
    return (reportEndpointEl?.getAttribute('data-has-filter') || '0') === '1';
  }

  function getSelectedTypes() {
    return Array.from(document.querySelectorAll('.type-cb'))
      .filter((cb) => cb.checked)
      .map((cb) => (cb.value || '').trim().toUpperCase())
      .filter(Boolean);
  }

  function setSelectedTypes(codes) {
    const set = new Set((codes || []).map((x) => String(x).toUpperCase()));
    document.querySelectorAll('.type-cb').forEach((cb) => {
      cb.checked = set.has(String(cb.value || '').toUpperCase());
    });
  }

  function getScope() {
    return document.querySelector('input[name="reportScope"]:checked')?.value || 'ativos_all';
  }

  function setScope(val) {
    const el = document.querySelector(`input[name="reportScope"][value="${val}"]`);
    if (el) el.checked = true;
  }

  function getOutput() {
    return document.querySelector('input[name="reportOutput"]:checked')?.value || 'pdf';
  }

  function setOutput(val) {
    const el = document.querySelector(`input[name="reportOutput"][value="${val}"]`);
    if (el) el.checked = true;
    syncOutputUI();
  }

  function getAction() {
    return document.querySelector('input[name="reportAction"]:checked')?.value || 'open';
  }

  function setAction(val) {
    const el = document.querySelector(`input[name="reportAction"][value="${val}"]`);
    if (el) el.checked = true;
  }

  function syncOutputUI() {
    const out = getOutput();
    const isZip = out === 'zip';

    if (zipHint) zipHint.style.display = isZip ? 'block' : 'none';

    const openRadio = document.querySelector('input[name="reportAction"][value="open"]');

    if (isZip) {
      setAction('download');
      if (openRadio) openRadio.disabled = true;
      if (actionOpenItem) actionOpenItem.style.opacity = '0.55';
    } else {
      if (openRadio) openRadio.disabled = false;
      if (actionOpenItem) actionOpenItem.style.opacity = '';
    }
  }

  document.querySelectorAll('input[name="reportOutput"]').forEach((r) => {
    r.addEventListener('change', () => {
      syncOutputUI();
      savePrefsIfNeeded();
    });
  });

  document.querySelectorAll('input[name="reportAction"]').forEach((r) => {
    r.addEventListener('change', () => savePrefsIfNeeded());
  });

  function presetDates(presetKey) {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = today.getMonth();

    function toYMD(d) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const da = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${da}`;
    }

    presets.forEach((b) => b.classList.toggle('active', b.getAttribute('data-preset') === presetKey));
    state.preset = presetKey || '';

    if (presetKey === 'total') {
      if (dtIniEl) dtIniEl.value = '';
      if (dtFimEl) dtFimEl.value = '';
      return;
    }

    let start = null;
    let end = null;

    if (presetKey === 'month_current') {
      start = new Date(yyyy, mm, 1);
      end = new Date(yyyy, mm, today.getDate());
    } else if (presetKey === 'month_prev') {
      const prevStart = new Date(yyyy, mm - 1, 1);
      const prevEnd = new Date(yyyy, mm, 0);
      start = prevStart;
      end = prevEnd;
    } else if (presetKey === 'last_30') {
      end = new Date(yyyy, mm, today.getDate());
      start = new Date(end);
      start.setDate(start.getDate() - 30);
    } else if (presetKey === 'year_current') {
      start = new Date(yyyy, 0, 1);
      end = new Date(yyyy, mm, today.getDate());
    }

    if (start && dtIniEl) dtIniEl.value = toYMD(start);
    if (end && dtFimEl) dtFimEl.value = toYMD(end);
  }

  presets.forEach((btn) => {
    btn.addEventListener('click', () => {
      presetDates(btn.getAttribute('data-preset'));
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  });

  function buildReportUrl(opts) {
    const baseUrl = getReportBaseUrl();
    const u = new URL(baseUrl, window.location.origin);

    if (opts.dt_ini) u.searchParams.set('dt_ini', opts.dt_ini);
    else u.searchParams.delete('dt_ini');

    if (opts.dt_fim) u.searchParams.set('dt_fim', opts.dt_fim);
    else u.searchParams.delete('dt_fim');

    u.searchParams.delete('types');
    (opts.types || []).forEach((t) => u.searchParams.append('types', t));

    u.searchParams.set('scope', opts.scope);
    u.searchParams.set('output', opts.output || 'pdf');

    if (opts.download === true) u.searchParams.set('download', '1');
    else u.searchParams.delete('download');

    u.searchParams.delete('q');
    u.searchParams.delete('status');

    if (opts.scope === 'filtered_all') {
      if (opts.q) u.searchParams.set('q', opts.q);
      u.searchParams.set('status', opts.status || 'ativos');
    }

    u.searchParams.delete('user_ids');
    if (opts.scope === 'selected') {
      (opts.user_ids || []).forEach((id) => u.searchParams.append('user_ids', id));
    }

    u.searchParams.set('fetch', '1');
    return u.toString();
  }

  function buildStatsQueryParams() {
    const scope = getScope();
    const q = getCurrentQ();
    const status = getCurrentStatus();
    const dtIni = (dtIniEl?.value || '').trim();
    const dtFim = (dtFimEl?.value || '').trim();
    const types = getSelectedTypes();
    const userIds = scope === 'selected' ? Array.from(state.manual.selected.keys()) : [];

    return { scope, q, status, dtIni, dtFim, types, userIds };
  }

  function openReportModal(options) {
    if (!reportModal) return;

    reportModal.classList.add('show');
    reportModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    if (!hasCurrentFilter()) {
      setScope('ativos_all');
    }

    applyPrefsIfAny();

    if (dtIniEl && !dtIniEl.value && dtFimEl && !dtFimEl.value) {
      presetDates('month_current');
    }

    if (options && options.preselectUserId) {
      setScope('selected');
      state.manual.selected.clear();
      state.manual.selected.set(String(options.preselectUserId), {
        id: Number(options.preselectUserId),
        nome: options.preselectUserName || 'Servidor',
        ativo: true
      });
      renderChips();
      updateManualSelectedCount();
      syncScopeUI(true);
    } else {
      syncScopeUI(false);
    }

    syncOutputUI();
    refreshPreview().catch(() => {});
  }

  function closeReportModal() {
    if (!reportModal) return;
    reportModal.classList.remove('show');
    reportModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  if (btnReport) {
    btnReport.addEventListener('click', (e) => {
      if (e.ctrlKey || e.metaKey || e.button === 1) return;
      e.preventDefault();
      openReportModal();
    });
  }

  if (reportCloseBtn) reportCloseBtn.addEventListener('click', closeReportModal);
  if (reportCancelBtn) reportCancelBtn.addEventListener('click', closeReportModal);

  if (reportModal) {
    reportModal.addEventListener('click', (event) => {
      if (event.target === reportModal) closeReportModal();
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && reportModal?.classList.contains('show')) {
      closeReportModal();
    }
  });

  document.querySelectorAll('input[name="reportScope"]').forEach((r) => {
    r.addEventListener('change', () => {
      syncScopeUI(false);
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  });

  document.querySelectorAll('.type-cb').forEach((cb) => {
    cb.addEventListener('change', () => {
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  });

  if (typesAllBtn) {
    typesAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.type-cb').forEach((cb) => (cb.checked = true));
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  }

  if (typesNoneBtn) {
    typesNoneBtn.addEventListener('click', () => {
      document.querySelectorAll('.type-cb').forEach((cb) => (cb.checked = false));
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  }

  // ===========================
  // Manual: busca e seleção
  // ===========================
  function updateManualSelectedCount() {
    if (!manualSelectedCountEl) return;
    manualSelectedCountEl.textContent = String(state.manual.selected.size || 0);
  }

  function renderChips() {
    if (!chipRow) return;

    const arr = Array.from(state.manual.selected.entries()).map(([id, u]) => ({
      id,
      nome: u?.nome || 'ID ' + id
    }));

    chipRow.innerHTML = arr.length
      ? arr.map((x) => {
          const safe = String(x.nome)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');

          return `
            <span class="chip" title="${safe}">
              <span class="name">${safe}</span>
              <button type="button" aria-label="Remover" data-id="${x.id}">
                <i class="fa-solid fa-xmark"></i>
              </button>
            </span>
          `;
        }).join('')
      : `<span class="muted" style="font-weight:800;">Nenhum selecionado.</span>`;

    chipRow.querySelectorAll('button[data-id]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = String(btn.getAttribute('data-id') || '');
        if (!id) return;

        state.manual.selected.delete(id);
        updateManualSelectedCount();
        renderChips();
        renderManualList();
        refreshPreview().catch(() => {});
      });
    });
  }

  function renderManualList() {
    if (!manualList) return;

    const items = state.manual.items || [];
    manualList.innerHTML = items.map((u) => {
      const id = String(u.id);
      const checked = state.manual.selected.has(id) ? 'checked' : '';
      const badgeClass = u.ativo ? 'on' : 'off';
      const badgeTxt = u.ativo ? 'Ativo' : 'Inativo';
      const safeName = (u.nome || 'Sem nome')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');

      return `
        <label class="pick-item">
          <input type="checkbox" class="manual-cb" data-id="${id}" ${checked}>
          <span class="pick-name">${safeName}</span>
          <span class="pick-badge ${badgeClass}">${badgeTxt}</span>
        </label>
      `;
    }).join('');

    manualList.querySelectorAll('.manual-cb').forEach((cb) => {
      cb.addEventListener('change', () => {
        const id = String(cb.getAttribute('data-id') || '');
        const u = (state.manual.items || []).find((x) => String(x.id) === id);
        if (!id || !u) return;

        if (cb.checked) state.manual.selected.set(id, u);
        else state.manual.selected.delete(id);

        updateManualSelectedCount();
        renderChips();
        refreshPreview().catch(() => {});
      });
    });

    if (manualResultsCountEl) manualResultsCountEl.textContent = String(state.manual.total || 0);
    if (manualPageLabelEl) manualPageLabelEl.textContent = String(state.manual.page || 1);
    if (manualPrevBtn) manualPrevBtn.disabled = state.manual.page <= 1;
    if (manualNextBtn) manualNextBtn.disabled = !state.manual.has_more;
  }

  async function fetchManualUsers(reset) {
    const searchUrl = getSearchUrl();
    if (!searchUrl) {
      showAlert('Rota de busca de usuários não configurada no template.', 'error');
      return;
    }

    const q = (userSearchInput?.value || '').trim();
    const st = (userSearchStatus?.value || 'ativos').trim();

    if (reset) state.manual.page = 1;

    const u = new URL(searchUrl, window.location.origin);
    u.searchParams.set('q', q);
    u.searchParams.set('status', st);
    u.searchParams.set('page', String(state.manual.page));
    u.searchParams.set('per_page', String(state.manual.per_page));

    try {
      const res = await fetch(u.toString(), { method: 'GET', credentials: 'same-origin' });
      if (!res.ok) {
        const txt = await res.text().catch(() => '');
        throw new Error(txt || ('Falha ao buscar usuários (HTTP ' + res.status + ').'));
      }

      const data = await res.json();

      state.manual.total = Number(data.total || 0);
      state.manual.items = Array.isArray(data.items) ? data.items : [];
      state.manual.has_more = !!data.has_more;
      state.manual.last_q = q;
      state.manual.last_status = st;

      renderManualList();
    } catch (err) {
      showAlert(err?.message || 'Não foi possível buscar usuários.', 'error');
    }
  }

  function syncScopeUI(forceFetch) {
    const scope = getScope();
    const isManual = scope === 'selected';

    if (manualWrap) manualWrap.classList.toggle('show', isManual);

    if (isManual) {
      renderChips();
      updateManualSelectedCount();
      if (forceFetch || (manualList && manualList.childElementCount === 0)) {
        state.manual.page = 1;
        fetchManualUsers(true);
      }
    }
  }

  function debounce(fn, ms) {
    let t = null;
    return function (...args) {
      if (t) clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  const debouncedSearch = debounce(() => {
    state.manual.page = 1;
    fetchManualUsers(true);
  }, 260);

  if (userSearchInput) {
    userSearchInput.addEventListener('input', () => {
      if (getScope() !== 'selected') return;
      debouncedSearch();
    });
  }

  if (userSearchStatus) {
    userSearchStatus.addEventListener('change', () => {
      if (getScope() !== 'selected') return;
      state.manual.page = 1;
      fetchManualUsers(true);
    });
  }

  if (manualPrevBtn) {
    manualPrevBtn.addEventListener('click', () => {
      if (state.manual.page <= 1) return;
      state.manual.page -= 1;
      fetchManualUsers(false);
    });
  }

  if (manualNextBtn) {
    manualNextBtn.addEventListener('click', () => {
      if (!state.manual.has_more) return;
      state.manual.page += 1;
      fetchManualUsers(false);
    });
  }

  if (manualClearBtn) {
    manualClearBtn.addEventListener('click', () => {
      state.manual.selected.clear();
      updateManualSelectedCount();
      renderChips();
      renderManualList();
      refreshPreview().catch(() => {});
    });
  }

  if (manualSelectPageBtn) {
    manualSelectPageBtn.addEventListener('click', () => {
      (state.manual.items || []).forEach((u) => {
        state.manual.selected.set(String(u.id), u);
      });
      updateManualSelectedCount();
      renderChips();
      renderManualList();
      refreshPreview().catch(() => {});
    });
  }

  async function selectAllResultsWithLimit(limit) {
    const searchUrl = getSearchUrl();
    const q = (userSearchInput?.value || '').trim();
    const st = (userSearchStatus?.value || 'ativos').trim();
    let page = 1;
    let picked = 0;

    while (picked < limit) {
      const u = new URL(searchUrl, window.location.origin);
      u.searchParams.set('q', q);
      u.searchParams.set('status', st);
      u.searchParams.set('page', String(page));
      u.searchParams.set('per_page', String(Math.min(80, state.manual.per_page)));

      const res = await fetch(u.toString(), { method: 'GET', credentials: 'same-origin' });
      if (!res.ok) break;

      const data = await res.json();
      const items = Array.isArray(data.items) ? data.items : [];

      for (const it of items) {
        state.manual.selected.set(String(it.id), it);
        picked += 1;
        if (picked >= limit) break;
      }

      if (!data.has_more || items.length === 0) break;
      page += 1;
    }

    updateManualSelectedCount();
    renderChips();
    renderManualList();
    return picked;
  }

  if (manualSelectAllResultsBtn) {
    manualSelectAllResultsBtn.addEventListener('click', async () => {
      const q = (userSearchInput?.value || '').trim();
      const st = (userSearchStatus?.value || 'ativos').trim();
      const msg = `Deseja selecionar TODOS os resultados desta busca?\n\nBusca: "${q || '—'}"\nStatus: ${st}\n\nIsso pode gerar um relatório grande.\n\n(Será aplicado um limite de segurança.)`;

      if (!confirm(msg)) return;

      try {
        showAlert('Selecionando resultados…', 'success');
        const picked = await selectAllResultsWithLimit(800);
        showAlert('Selecionados: ' + picked + ' usuário(s).', 'success');
        refreshPreview().catch(() => {});
      } catch (err) {
        showAlert(err?.message || 'Não foi possível selecionar todos os resultados.', 'error');
      }
    });
  }

  // ===========================
  // Prévia
  // ===========================
  function humanTypeOrder(types) {
    const order = ['AB', 'BH', 'TRE', 'LM', 'DL', 'DS', 'FS', 'OUTROS'];
    const set = new Set(types || []);
    return order.filter((x) => set.has(x)).concat((types || []).filter((x) => !order.includes(x)));
  }

  function formatBreakdown(counts, selectedTypes) {
    const types = humanTypeOrder(selectedTypes || []);
    const parts = [];
    for (const t of types) {
      const v = Number((counts && counts[t]) || 0);
      parts.push(`${t}: ${v}`);
    }
    return parts.join(' · ');
  }

  async function refreshPreview() {
    if (!pvUsersEl || !pvRegsEl || !pvDetailEl) return;

    pvUsersEl.textContent = '…';
    pvRegsEl.textContent = '…';
    pvDetailEl.textContent = 'Calculando…';

    const countUrl = getCountUrl();
    if (!countUrl) {
      pvUsersEl.textContent = '—';
      pvRegsEl.textContent = '—';
      pvDetailEl.textContent = 'Endpoint de contagem não configurado.';
      return;
    }

    const { scope, q, status, dtIni, dtFim, types, userIds } = buildStatsQueryParams();

    if (scope === 'selected' && userIds.length === 0) {
      pvUsersEl.textContent = '0';
      pvRegsEl.textContent = '—';
      pvDetailEl.textContent = 'Seleção manual vazia.';
      return;
    }

    try {
      const u = new URL(countUrl, window.location.origin);
      u.searchParams.set('scope', scope);

      if (scope === 'filtered_all') {
        if (q) u.searchParams.set('q', q);
        u.searchParams.set('status', status);
      }

      if (scope === 'selected') {
        userIds.forEach((id) => u.searchParams.append('user_ids', id));
      }

      const res = await fetch(u.toString(), { method: 'GET', credentials: 'same-origin' });
      if (!res.ok) throw new Error('Falha ao consultar contagem de usuários.');

      const data = await res.json();
      const totalUsers = Number(data.total || 0);
      pvUsersEl.textContent = String(totalUsers);
    } catch {
      pvUsersEl.textContent = '—';
    }

    const statsUrl = getStatsUrl();
    if (!statsUrl) {
      pvRegsEl.textContent = '—';
      pvDetailEl.textContent = 'Endpoint de prévia (stats) não configurado.';
      return;
    }

    try {
      const s = new URL(statsUrl, window.location.origin);
      s.searchParams.set('scope', scope);

      if (dtIni) s.searchParams.set('dt_ini', dtIni);
      if (dtFim) s.searchParams.set('dt_fim', dtFim);

      s.searchParams.delete('types');
      (types || []).forEach((t) => s.searchParams.append('types', t));

      if (scope === 'filtered_all') {
        if (q) s.searchParams.set('q', q);
        s.searchParams.set('status', status || 'ativos');
      }

      if (scope === 'selected') {
        userIds.forEach((id) => s.searchParams.append('user_ids', id));
      }

      const res2 = await fetch(s.toString(), { method: 'GET', credentials: 'same-origin' });
      if (!res2.ok) {
        const txt = await res2.text().catch(() => '');
        throw new Error(txt || ('Prévia de registros indisponível (HTTP ' + res2.status + ').'));
      }

      const stats = await res2.json().catch(() => ({}));
      if (!stats || stats.success === false) {
        throw new Error((stats && stats.error) || 'Prévia de registros indisponível.');
      }

      const recordsTotal = Number(stats.records_total ?? stats.total_records ?? stats.total ?? 0);
      const countsByType = stats.counts_by_type || stats.by_type || stats.counts || {};

      pvRegsEl.textContent = String(recordsTotal);
      const breakdown = formatBreakdown(countsByType, types);

      if (breakdown && breakdown.trim()) {
        pvDetailEl.textContent = breakdown;
      } else {
        pvDetailEl.textContent = 'Sem detalhes por tipo (backend não retornou breakdown).';
      }
    } catch (e) {
      pvRegsEl.textContent = '—';
      pvDetailEl.textContent = e?.message || 'Falha ao calcular registros estimados.';
    }
  }

  if (pvRefreshBtn) {
    pvRefreshBtn.addEventListener('click', () => refreshPreview());
  }

  // ===========================
  // Preferências
  // ===========================
  function savePrefsIfNeeded() {
    if (!rememberPrefsCb || !rememberPrefsCb.checked) return;

    const prefs = {
      preset: state.preset || '',
      dt_ini: dtIniEl?.value || '',
      dt_fim: dtFimEl?.value || '',
      scope: getScope(),
      types: getSelectedTypes(),
      output: getOutput(),
      action: getAction(),
      manual_status: userSearchStatus?.value || 'ativos'
    };

    try {
      localStorage.setItem(PREF_KEY, JSON.stringify(prefs));
    } catch {}
  }

  function applyPrefsIfAny() {
    let raw = null;
    try {
      raw = localStorage.getItem(PREF_KEY);
    } catch {}

    if (!raw) return;

    let prefs = null;
    try {
      prefs = JSON.parse(raw);
    } catch {
      return;
    }

    if (!prefs) return;

    if (prefs.preset) {
      presetDates(prefs.preset);
    } else {
      if (dtIniEl && typeof prefs.dt_ini === 'string') dtIniEl.value = prefs.dt_ini;
      if (dtFimEl && typeof prefs.dt_fim === 'string') dtFimEl.value = prefs.dt_fim;
    }

    if (prefs.scope) {
      if (prefs.scope === 'filtered_all' && !hasCurrentFilter()) {
        setScope('ativos_all');
      } else {
        setScope(prefs.scope);
      }
    }

    if (Array.isArray(prefs.types) && prefs.types.length) setSelectedTypes(prefs.types);
    if (prefs.output) setOutput(prefs.output);
    if (prefs.action) setAction(prefs.action);

    if (userSearchStatus && prefs.manual_status) {
      userSearchStatus.value = prefs.manual_status;
    }
  }

  if (rememberPrefsCb) {
    rememberPrefsCb.addEventListener('change', () => {
      if (!rememberPrefsCb.checked) {
        try {
          localStorage.removeItem(PREF_KEY);
        } catch {}
      } else {
        savePrefsIfNeeded();
      }
    });
  }

  if (dtIniEl) {
    dtIniEl.addEventListener('change', () => {
      state.preset = '';
      presets.forEach((b) => b.classList.remove('active'));
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  }

  if (dtFimEl) {
    dtFimEl.addEventListener('change', () => {
      state.preset = '';
      presets.forEach((b) => b.classList.remove('active'));
      savePrefsIfNeeded();
      refreshPreview().catch(() => {});
    });
  }

  // ==========================================================
  // GERAR RELATÓRIO (MODAL)
  // ==========================================================
  if (reportGenerateBtn) {
    reportGenerateBtn.addEventListener('click', async () => {
      const baseUrl = getReportBaseUrl();
      if (!baseUrl) {
        showAlert('Endpoint do relatório não encontrado.', 'error');
        return;
      }

      const dtIni = (dtIniEl?.value || '').trim();
      const dtFim = (dtFimEl?.value || '').trim();

      if (dtIni && dtFim && dtIni > dtFim) {
        showAlert('Período inválido: a data inicial é maior que a data final.', 'error');
        return;
      }

      const types = getSelectedTypes();
      if (!types.length) {
        showAlert('Selecione ao menos um tipo para o relatório.', 'error');
        return;
      }

      const scope = getScope();
      const output = getOutput();
      const action = getAction();

      const q = getCurrentQ();
      const status = getCurrentStatus();

      let userIds = [];
      if (scope === 'selected') {
        userIds = Array.from(state.manual.selected.keys());
        if (!userIds.length) {
          showAlert('Selecione ao menos um usuário na seleção manual.', 'error');
          return;
        }
      }

      const isDownload = action === 'download' || output === 'zip';
      const url = buildReportUrl({
        dt_ini: dtIni,
        dt_fim: dtFim,
        types,
        scope,
        q,
        status,
        user_ids: userIds,
        output,
        download: isDownload
      });

      savePrefsIfNeeded();
      reportGenerateBtn.classList.add('is-loading');

      activeAbortController = new AbortController();

      const niceMode = output === 'zip'
        ? 'ZIP (1 PDF por servidor)'
        : 'PDF consolidado';

      const niceScope =
        scope === 'selected'
          ? `Selecionados (${userIds.length})`
          : scope === 'filtered_all'
            ? 'Resultados da busca'
            : scope === 'ativos_all'
              ? 'Todos ativos'
              : 'Todos';

      startProgress({
        title: 'Gerando relatório…',
        sub: `${niceMode} • Escopo: ${niceScope}`,
        startPct: 6,
        cap: output === 'zip' ? 84 : 88
      });

      try {
        const fallbackName = output === 'zip'
          ? 'relatorios_prontuarios.zip'
          : 'relatorio_servidores.pdf';

        const mode = isDownload ? 'download' : 'open';

        setProgress(Math.max(progressValue, 10), 'Enviando solicitação…');

        await downloadFile(url, fallbackName, {
          signal: activeAbortController.signal,
          mode,
          onStage: (stage) => {
            setProgress(Math.max(progressValue, 12), stage);
          },
          onDownloadProgress: (received, total) => {
            if (total > 0) {
              const pct = Math.min(99, Math.max(0, (received / total) * 100));
              const mapped = 88 + (pct * 0.11);
              setProgress(Math.max(progressValue, mapped), 'Baixando arquivo…');
            } else {
              setProgress(Math.max(progressValue, 88), 'Baixando arquivo…');
            }
          }
        });

        if (mode === 'open') {
          finishProgressSuccess('Relatório aberto em nova aba.', 'Abertura concluída.');
          showAlert('Relatório aberto em nova aba.', 'success');
        } else {
          finishProgressSuccess('Arquivo gerado e baixado.', 'Download concluído.');
          showAlert('Arquivo gerado e baixado com sucesso.', 'success');
        }

        closeReportModal();
      } catch (err) {
        if (err && (err.name === 'AbortError' || /aborted/i.test(String(err.message || '')))) {
          finishProgressError('Cancelado pelo usuário.');
          showAlert('Geração cancelada.', 'error');
        } else {
          finishProgressError(err?.message || 'Não foi possível gerar.');
          showAlert(err?.message || 'Não foi possível gerar o relatório.', 'error');
        }
      } finally {
        activeAbortController = null;
        reportGenerateBtn.classList.remove('is-loading');
      }
    });
  }

  // ==========================================================
  // INICIALIZAÇÕES
  // ==========================================================
  syncOutputUI();
});