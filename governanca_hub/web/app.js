/* Front-End Controller do Hub Executivo de Governança e Business Analytics */

let hubTelemetry = null;
let currentFilter = 'ALL';

document.addEventListener('DOMContentLoaded', async () => {
  await loadTelemetryFromBackend();
  await runLiveSimulation();
});

function switchView(viewId, buttonElement) {
  document.querySelectorAll('.view-section').forEach(section => {
    section.classList.remove('active');
  });
  document.querySelectorAll('.nav-pill').forEach(pill => {
    pill.classList.remove('active');
  });

  const target = document.getElementById(viewId);
  if (target) {
    target.classList.add('active');
  }
  if (buttonElement) {
    buttonElement.classList.add('active');
  }
}

function toggleTheme() {
  document.body.classList.toggle('light-theme');
  const btn = document.getElementById('themeToggleBtn');
  if (document.body.classList.contains('light-theme')) {
    btn.textContent = '🌙 Tema Escuro';
  } else {
    btn.textContent = '☀️ Tema Claro';
  }
}

async function loadTelemetryFromBackend() {
  try {
    const response = await fetch('/api/telemetry');
    hubTelemetry = await response.json();
    renderModulesBentoGrid();
    populateCvSamplesSelector();
    renderIotAnalyticsComparison();
    renderGovernanceAuditCards();
  } catch (err) {
    console.error('Erro ao carregar telemetria do Hub:', err);
  }
}

function filterModules(filterType, buttonEl) {
  currentFilter = filterType;
  document.querySelectorAll('.filter-chip').forEach(chip => chip.classList.remove('active'));
  if (buttonEl) buttonEl.classList.add('active');
  renderModulesBentoGrid();
}

function renderModulesBentoGrid() {
  if (!hubTelemetry || !hubTelemetry.modules) return;
  const container = document.getElementById('modulesBentoGrid');
  const filtered = hubTelemetry.modules.filter(mod => {
    if (currentFilter === 'INTEGRATED') return mod.integration_status.includes('Integrado');
    if (currentFilter === 'VERTICAL') return mod.integration_status.includes('Vertical');
    return true;
  });

  container.innerHTML = filtered.map(mod => {
    const isIntegrated = mod.integration_status.includes('Integrado');
    const badgeClass = isIntegrated ? 'integrated' : 'vertical';
    const badgeLabel = isIntegrated ? '🟢 Integrado ZelaIA' : '🔵 Vertical Governada';
    const sdgHtml = (mod.sdg_goals || []).map(sdg => `<span class="sdg-pill">${sdg}</span>`).join('');

    return `
      <article class="module-card" onclick="openModuleModal('${mod.module_id}')">
        <div>
          <div class="card-top-meta">
            <span class="status-badge ${badgeClass}">${badgeLabel}</span>
            <span class="folder-tag">${mod.folder_name}</span>
          </div>
          <div style="margin-top: 12px;">
            <div class="module-discipline">${mod.discipline_name}</div>
            <h3 class="module-title">${mod.project_title}</h3>
          </div>
        </div>

        <div class="module-metrics-pair">
          <div>
            <span class="mini-metric-label">${mod.main_metric_label}</span>
            <span class="mini-metric-val">${mod.main_metric_value}</span>
          </div>
          <div>
            <span class="mini-metric-label">${mod.secondary_metric_label}</span>
            <span class="mini-metric-val">${mod.secondary_metric_value}</span>
          </div>
        </div>

        <p class="module-reason">${mod.integration_justification}</p>

        <div class="card-footer-row">
          <div class="sdg-pills">${sdgHtml}</div>
          <button class="inspect-btn">Ficha &amp; Evidências ↗</button>
        </div>
      </article>
    `;
  }).join('');
}

function populateCvSamplesSelector() {
  if (!hubTelemetry || !hubTelemetry.cv_samples) return;
  const selectEl = document.getElementById('simCvSelect');
  selectEl.innerHTML = hubTelemetry.cv_samples.map((sample, index) => {
    const tag = sample.is_crack ? '🔴 Com Fissura' : '🟢 Normal (Sem Fissura)';
    return `<option value="${index}">${tag} — ${sample.name}</option>`;
  }).join('');
  updateCvSimulator();
}

function updateCvSimulator() {
  if (!hubTelemetry || !hubTelemetry.cv_samples || hubTelemetry.cv_samples.length === 0) return;
  const selectEl = document.getElementById('simCvSelect');
  const shadowMode = document.getElementById('simShadowToggle').checked;
  const index = parseInt(selectEl.value || '0', 10);
  const sample = hubTelemetry.cv_samples[index] || hubTelemetry.cv_samples[0];

  const imgEl = document.getElementById('simCvImage');
  imgEl.src = sample.url;

  const threshold = shadowMode ? 0.35 : 0.50;
  const prob = sample.is_crack ? (shadowMode ? 97.6 : 99.4) : 0.8;
  const badgeEl = document.getElementById('simCvResultBadge');
  const probBar = document.getElementById('simCvProbBar');
  const metaEl = document.getElementById('simCvMetaText');

  if (sample.is_crack) {
    badgeEl.innerHTML = `<span class="status-badge integrated" style="background:rgba(244,63,94,0.16); color:#fb7185; border-color:rgba(244,63,94,0.4);">⚠️ FISSURA DETECTADA (${prob.toFixed(1)}%) • Priorizar Vistoria</span>`;
    probBar.className = 'bar-fill rose';
    probBar.style.width = `${prob}%`;
  } else {
    badgeEl.innerHTML = `<span class="status-badge integrated">✅ SUPERFÍCIE ÍNTEGRA (${(100 - prob).toFixed(1)}% Normal)</span>`;
    probBar.className = 'bar-fill emerald';
    probBar.style.width = '100%';
  }

  metaEl.innerHTML = `Limiar ativo: <strong>T = ${threshold.toFixed(2)}</strong> ${shadowMode ? '(Recall sob sombra sobe de 89,4% para 97,6%)' : '(Padrão ideal)'} • Triagem 2D preventiva.`;
}

function setLgpdPreset(presetId) {
  const inputEl = document.getElementById('simLgpdInput');
  if (presetId === 1) {
    inputEl.value = 'Sou morador de São Paulo, meu CPF é 412.890.123-45, telefone (11) 98877-6655 e e-mail cidadao.teste@email.com. A calçada e o muro em frente à escola estão com fissura no concreto e bueiro entupido na chuva.';
  } else {
    inputEl.value = 'A rampa de cadeirantes na esquina da unidade básica de saúde cedeu com a chuva forte de hoje e há risco de queda para idosos.';
  }
  runLiveSimulation();
}

async function runLiveSimulation() {
  const rawText = document.getElementById('simLgpdInput').value;
  const taskCount = parseInt(document.getElementById('simClusterSlider').value || '1000', 10);
  const budgetHours = parseInt(document.getElementById('simQuantumSlider').value || '8', 10);

  document.getElementById('simClusterCountLabel').textContent = `${taskCount.toLocaleString('pt-BR')} fotos`;
  document.getElementById('simQuantumHoursLabel').textContent = `${budgetHours} horas`;

  try {
    const response = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        raw_text: rawText,
        task_count: taskCount,
        budget_hours: budgetHours
      })
    });
    const result = await response.json();

    // 1. Atualiza LGPD
    const highlighted = result.sanitized_text
      .replace(/\[CPF PROTEGIDO - LGPD\]/g, '<span class="masked-token">[CPF PROTEGIDO - LGPD]</span>')
      .replace(/\[EMAIL PROTEGIDO - LGPD\]/g, '<span class="masked-token">[EMAIL PROTEGIDO - LGPD]</span>')
      .replace(/\[TELEFONE PROTEGIDO - LGPD\]/g, '<span class="masked-token">[TELEFONE PROTEGIDO - LGPD]</span>');
    document.getElementById('simLgpdOutput').innerHTML = highlighted || '<em>Digite um relato acima...</em>';
    const counts = result.masked_counts || { CPF: 0, EMAIL: 0, TELEFONE: 0 };
    document.getElementById('simLgpdCounters').innerHTML =
      `🔒 Dados Pessoais Interceptados: <strong>CPF (${counts.CPF})</strong> • <strong>Telefone (${counts.TELEFONE})</strong> • <strong>E-mail (${counts.EMAIL})</strong>`;

    // 2. Atualiza Cluster iSPD
    const cluster = result.cluster;
    document.getElementById('simClusterWorkloadLabel').textContent =
      `${cluster.total_mflop.toLocaleString('pt-BR')} MFLOP | ${cluster.total_network_mbit.toLocaleString('pt-BR')} Mbit`;
    document.getElementById('simCluster2WText').textContent = `${cluster.time_2_workers_seconds.toFixed(2)} s`;
    document.getElementById('simCluster4WText').textContent =
      `${cluster.time_4_workers_seconds.toFixed(2)} s (-${cluster.time_saved_seconds.toFixed(2)} s)`;

    // 3. Atualiza Otimização Quântica
    const opt = result.optimization;
    document.getElementById('simGreedyScore').textContent = `${opt.greedy_total_priority} pts (${opt.greedy_total_hours}h)`;
    document.getElementById('simGreedyItems').textContent = `Escolhe: ${opt.greedy_selected_codes.join(' + ') || 'Nenhum'}`;
    document.getElementById('simOptimalScore').textContent = `${opt.optimal_total_priority} pts (${opt.optimal_total_hours}h)`;
    document.getElementById('simOptimalItems').textContent =
      `Escolhe: ${opt.optimal_selected_codes.join(' + ') || 'Nenhum'} (+${opt.priority_gain} pts)`;

    const verdictEl = document.getElementById('simQuantumVerdict');
    if (opt.priority_gain > 0) {
      verdictEl.innerHTML = `✅ Com <strong>${budgetHours}h</strong>, a formulação combinatória / QAOA supera a heurística gulosa em <strong>+${opt.priority_gain} pontos de prioridade</strong> (${opt.optimal_selected_codes.join('+')} vs ${opt.greedy_selected_codes.join('+')}).`;
    } else {
      verdictEl.innerHTML = `ℹ️ Para o limite de <strong>${budgetHours}h</strong>, ambos os métodos atingem <strong>${opt.optimal_total_priority} pontos</strong>.`;
    }
  } catch (err) {
    console.error('Erro na simulação:', err);
  }
}

function renderIotAnalyticsComparison() {
  if (!hubTelemetry || !hubTelemetry.iot_telemetry) return;
  const rows = hubTelemetry.iot_telemetry.synthetic_comparison_table || [];
  const container = document.getElementById('iotAnalyticsTableContainer');

  const rowsHtml = rows.map(r => `
    <div style="display:grid; grid-template-columns: 1.3fr 1fr 1fr 1fr; gap:8px; padding:9px 12px; background:var(--bg-subtle); border-radius:8px; margin-bottom:8px; font-size:0.81rem; align-items:center;">
      <strong>${r.condition}</strong>
      <span style="font-family:'JetBrains Mono',monospace;">Studio: ${r.studio_08_int8.toFixed(1)}%</span>
      <span style="font-family:'JetBrains Mono',monospace; color:var(--accent-cyan);">Base: ${r.public_base.toFixed(1)}%</span>
      <span style="font-family:'JetBrains Mono',monospace; color:var(--accent-emerald); font-weight:700;">+Sint: ${r.plus_synthetics.toFixed(1)}%</span>
    </div>
  `).join('');

  container.innerHTML = `
    <div style="display:grid; grid-template-columns: 1.3fr 1fr 1fr 1fr; gap:8px; padding:4px 12px; font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; font-weight:700;">
      <span>Condição Sonora</span>
      <span>08 int8 Studio</span>
      <span>PyTorch Público</span>
      <span>PyTorch + Sintéticos</span>
    </div>
    ${rowsHtml}
  `;
}

function renderGovernanceAuditCards() {
  if (!hubTelemetry || !hubTelemetry.modules) return;
  const container = document.getElementById('governanceCardsGrid');
  container.innerHTML = hubTelemetry.modules.map(mod => {
    const isIntegrated = mod.integration_status.includes('Integrado');
    const badgeClass = isIntegrated ? 'integrated' : 'vertical';
    return `
      <div class="sim-card" style="cursor:pointer;" onclick="openModuleModal('${mod.module_id}')">
        <div class="card-top-meta">
          <span class="status-badge ${badgeClass}">${mod.folder_name}</span>
          <span class="folder-tag">${mod.discipline_name}</span>
        </div>
        <h3 class="module-title">${mod.project_title}</h3>
        <div class="gov-pillars-grid" style="margin:6px 0;">
          <div class="gov-pillar-box">
            <h5>🔒 Proteção LGPD</h5>
            <p>${mod.lgpd_mechanism}</p>
          </div>
          <div class="gov-pillar-box">
            <h5>👤 Revisão Humana</h5>
            <p>${mod.human_in_the_loop_mechanism}</p>
          </div>
          <div class="gov-pillar-box">
            <h5>🛡️ Controle &amp; Limite</h5>
            <p>${mod.known_limitations}</p>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function openModuleModal(moduleId) {
  if (!hubTelemetry || !hubTelemetry.modules) return;
  const mod = hubTelemetry.modules.find(m => m.module_id === moduleId);
  if (!mod) return;

  const isIntegrated = mod.integration_status.includes('Integrado');
  const badgeEl = document.getElementById('modalStatusBadge');
  badgeEl.className = `status-badge ${isIntegrated ? 'integrated' : 'vertical'}`;
  badgeEl.textContent = mod.integration_status;

  document.getElementById('modalFolderTag').textContent = mod.folder_name;
  document.getElementById('modalTitle').textContent = `${mod.discipline_name} — ${mod.project_title}`;
  document.getElementById('modalStack').textContent = `Stack: ${mod.primary_technology_stack}`;

  const filesHtml = (mod.verified_files || []).map(f => `<span class="file-chip">📄 ${f}</span>`).join('');
  const imagesHtml = (mod.evidence_images || []).map(img => `
    <div class="evidence-card">
      <img src="${img.url}" alt="${img.label}" loading="lazy" />
      <span>${img.label}</span>
    </div>
  `).join('');

  const extraIotBanner = mod.studio_url ? `
    <div style="background:rgba(56,189,248,0.1); border:1px solid var(--border-highlight); padding:12px 16px; border-radius:10px; margin-bottom:16px; font-size:0.84rem;">
      🔗 <strong>Projeto Oficial no Edge Impulse Studio:</strong>
      <a href="${mod.studio_url}" target="_blank" style="color:var(--accent-cyan); margin-left:6px;">${mod.studio_url}</a>
      • <strong>Hardware Alvo:</strong> <code>${mod.target_mcu}</code>
    </div>
  ` : '';

  document.getElementById('modalBodyContent').innerHTML = `
    ${extraIotBanner}
    <div class="module-metrics-pair" style="margin-bottom: 16px;">
      <div>
        <span class="mini-metric-label">${mod.main_metric_label}</span>
        <span class="mini-metric-val" style="font-size:1.05rem;">${mod.main_metric_value}</span>
      </div>
      <div>
        <span class="mini-metric-label">${mod.secondary_metric_label}</span>
        <span class="mini-metric-val" style="font-size:1.05rem;">${mod.secondary_metric_value}</span>
      </div>
    </div>

    <div class="gov-pillars-grid">
      <div class="gov-pillar-box">
        <h5>🔒 Conformidade LGPD</h5>
        <p>${mod.lgpd_mechanism}</p>
      </div>
      <div class="gov-pillar-box">
        <h5>👤 Human-in-the-Loop (Art. 20)</h5>
        <p>${mod.human_in_the_loop_mechanism}</p>
      </div>
      <div class="gov-pillar-box">
        <h5>🛡️ Guardrails &amp; Anti-Leakage</h5>
        <p>${mod.hallucination_or_error_control}</p>
      </div>
    </div>

    <div class="gov-pillar-box" style="margin-bottom: 16px;">
      <h5>🧭 Justificativa Arquitetural de Integração &amp; Limites Declarados</h5>
      <p><strong>Arquitetura:</strong> ${mod.integration_justification}</p>
      <p style="margin-top:6px;"><strong>Limite Operacional:</strong> ${mod.known_limitations}</p>
    </div>

    ${imagesHtml ? `
      <h4 style="font-size:0.95rem; margin: 16px 0 8px 0;">🖼️ Evidências Visuais e Capturas Reais da Pasta (${mod.folder_name})</h4>
      <div class="evidence-gallery">${imagesHtml}</div>
    ` : ''}

    <h4 style="font-size:0.95rem; margin: 18px 0 8px 0;">📂 Artefatos Verificados no Repositório (${mod.folder_name})</h4>
    <div class="file-list-chip-grid">${filesHtml}</div>
  `;

  document.getElementById('moduleModalBackdrop').classList.add('open');
}

function closeModuleModal(event) {
  if (event && event.target && event.target.id !== 'moduleModalBackdrop') return;
  document.getElementById('moduleModalBackdrop').classList.remove('open');
}
