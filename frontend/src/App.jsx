
import { useEffect, useState } from 'react';
import './App.css';

const API = 'http://localhost:5000/api';

function App() {
  const [cidade, setCidade] = useState('');
  const [historico, setHistorico] = useState([]);
  const [consultaId, setConsultaId] = useState('');
  const [previsoes, setPrevisoes] = useState([]);
  const [climaAtual, setClimaAtual] = useState(null);
  const [previsaoRapida, setPrevisaoRapida] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');
  const [mensagem, setMensagem] = useState('');

  useEffect(() => {
    carregarHistorico();
  }, []);

  async function carregarHistorico() {
    try {
      const resposta = await fetch(`${API}/historico`);
      if (!resposta.ok) throw new Error('Não foi possível carregar o histórico.');

      const dados = await resposta.json();
      setHistorico(dados);

      if (dados.length > 0) {
        setConsultaId(String(dados[0].id));
        carregarClima(dados[0].id);
      }
    } catch (error) {
      setErro('Não foi possível conectar à API. Verifique se o backend está ligado.');
    }
  }

  async function carregarClima(id) {
    if (!id) return;

    setConsultaId(String(id));
    setErro('');
    setMensagem('');

    try {
      const resposta = await fetch(`${API}/clima/${id}`);
      const dados = await resposta.json();

      if (!resposta.ok) {
        setPrevisoes([]);
        setMensagem('Os dados consolidados ainda não estão disponíveis. Execute a exportação e o pipeline do Apache Hop.');
        return;
      }

      setPrevisoes(dados.previsoes || []);
      setClimaAtual(null);
      setPrevisaoRapida([]);
    } catch {
      setErro('Erro ao buscar os dados climáticos.');
    }
  }

  async function consultarCidade(event) {
    event.preventDefault();

    if (!cidade.trim()) {
      setErro('Digite o nome de uma cidade.');
      return;
    }

    setCarregando(true);
    setErro('');
    setMensagem('');
    setPrevisoes([]);
    setClimaAtual(null);
    setPrevisaoRapida([]);

    try {
      const resposta = await fetch(`${API}/consultas`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cidade })
      });

      const dados = await resposta.json();

      if (!resposta.ok) {
        throw new Error(dados.erro || 'Não foi possível realizar a consulta.');
      }

      setConsultaId(String(dados.consulta_id));
      setClimaAtual(dados.clima_atual);

      const diario = dados.previsao_diaria;

      if (diario) {
        const lista = diario.time.map((data, index) => ({
          data,
          temp_min: diario.temperature_2m_min[index],
          temp_max: diario.temperature_2m_max[index]
        }));

        setPrevisaoRapida(lista);
      }

      setMensagem(
        `Consulta registrada com sucesso! ID ${dados.consulta_id}. Os dados foram armazenados e aguardam a consolidação pelo Apache Hop.`
      );

      await carregarHistorico();
    } catch (error) {
      setErro(error.message || 'Erro ao consultar a cidade.');
    } finally {
      setCarregando(false);
    }
  }

  function formatarData(data) {
    if (!data) return '-';

    return new Date(`${String(data).slice(0, 10)}T12:00:00`)
      .toLocaleDateString('pt-BR');
  }

  function formatarNumero(valor, unidade = '') {
    if (valor === null || valor === undefined || valor === '') return '-';
    return `${Number(valor).toLocaleString('pt-BR', {
      maximumFractionDigits: 1
    })}${unidade}`;
  }

  const nomeCidade = historico.find(
    (item) => String(item.id) === String(consultaId)
  )?.cidade;

  return (
    <main className="app">
      <header className="topbar">
        <div className="logo">
          <div className="logo-icon">☀</div>
          <div>
            <strong>AgroClima</strong>
            <span>INTELIGENTE</span>
          </div>
        </div>

        <div className="status-api">
          <span className="status-dot"></span>
          Sistema de monitoramento climático
        </div>
      </header>

      <section className="welcome">
        <div>
          <span className="eyebrow">PAINEL DE MONITORAMENTO</span>
          <h1>Clima e agricultura em um só lugar.</h1>
          <p>
            Consulte condições meteorológicas, acompanhe previsões e
            visualize os dados climáticos integrados.
          </p>
        </div>
        <div className="welcome-icon">🌤️</div>
      </section>

      <section className="search-section">
        <div>
          <h2>Consultar cidade</h2>
          <p>Digite uma cidade para buscar os dados meteorológicos.</p>
        </div>

        <form onSubmit={consultarCidade} className="search-form">
          <input
            type="text"
            placeholder="Ex.: São João da Boa Vista"
            value={cidade}
            onChange={(event) => setCidade(event.target.value)}
          />
          <button type="submit" disabled={carregando}>
            {carregando ? 'Consultando...' : 'Consultar clima'}
          </button>
        </form>

        {erro && <div className="alert error">{erro}</div>}
        {mensagem && <div className="alert success">{mensagem}</div>}
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">ACOMPANHAMENTO</span>
            <h2>Dados climáticos</h2>
            <p>
              {nomeCidade || 'Selecione uma consulta no histórico.'}
              {consultaId ? ` · Consulta #${consultaId}` : ''}
            </p>
          </div>

          {historico.length > 0 && (
            <select
              value={consultaId}
              onChange={(event) => carregarClima(event.target.value)}
            >
              {historico.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.cidade} — #{item.id}
                </option>
              ))}
            </select>
          )}
        </div>

        {climaAtual && (
          <div className="weather-grid">
            <article className="weather-card highlight">
              <span>Temperatura atual</span>
              <strong>
                {formatarNumero(climaAtual.temperature_2m, ' °C')}
              </strong>
              <small>Condição no momento da consulta</small>
              <div className="weather-icon">🌡️</div>
            </article>

            <article className="weather-card">
              <span>Umidade do ar</span>
              <strong>
                {formatarNumero(climaAtual.relative_humidity_2m, '%')}
              </strong>
              <small>Umidade relativa atual</small>
              <div className="weather-icon">💧</div>
            </article>

            <article className="weather-card">
              <span>Precipitação atual</span>
              <strong>
                {formatarNumero(climaAtual.precipitation, ' mm')}
              </strong>
              <small>Volume de chuva registrado</small>
              <div className="weather-icon">🌧️</div>
            </article>
          </div>
        )}

        {previsaoRapida.length > 0 && (
          <div className="data-card">
            <div className="table-heading">
              <h3>Previsão diária</h3>
              <span className="tag">Consulta da API</span>
            </div>

            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Temperatura mínima</th>
                    <th>Temperatura máxima</th>
                  </tr>
                </thead>
                <tbody>
                  {previsaoRapida.map((item) => (
                    <tr key={item.data}>
                      <td>{formatarData(item.data)}</td>
                      <td>{formatarNumero(item.temp_min, ' °C')}</td>
                      <td>{formatarNumero(item.temp_max, ' °C')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {previsoes.length > 0 && (
          <div className="data-card">
            <div className="table-heading">
              <h3>Previsões consolidadas</h3>
              <span className="tag integrated">MySQL · Apache Hop</span>
            </div>

            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Mínima</th>
                    <th>Máxima</th>
                    <th>Prob. de chuva</th>
                    <th>Precipitação</th>
                  </tr>
                </thead>
                <tbody>
                  {previsoes.map((item) => (
                    <tr key={item.data_previsao}>
                      <td>{formatarData(item.data_previsao)}</td>
                      <td>{formatarNumero(item.temp_min, ' °C')}</td>
                      <td>{formatarNumero(item.temp_max, ' °C')}</td>
                      <td>{formatarNumero(item.prob_chuva_max, '%')}</td>
                      <td>{formatarNumero(item.precipitacao_mm, ' mm')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!climaAtual && previsoes.length === 0 && !mensagem && (
          <div className="empty-state">
            <span>🌦️</span>
            <strong>Nenhum dado carregado</strong>
            <p>Faça uma consulta ou selecione um registro do histórico.</p>
          </div>
        )}
      </section>

      <section className="section history-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">REGISTROS ANTERIORES</span>
            <h2>Histórico de consultas</h2>
            <p>Consultas armazenadas no banco de dados MySQL.</p>
          </div>
          <span className="history-count">{historico.length} registros</span>
        </div>

        <div className="data-card">
          {historico.length > 0 ? (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Cidade</th>
                    <th>País</th>
                    <th>Data da consulta</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {historico.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <strong>{item.cidade}</strong>
                      </td>
                      <td>{item.pais || '-'}</td>
                      <td>
                        {item.data_consulta
                          ? new Date(item.data_consulta).toLocaleString('pt-BR')
                          : '-'}
                      </td>
                      <td>
                        <button
                          className="view-button"
                          onClick={() => carregarClima(item.id)}
                        >
                          Visualizar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-history">
              Ainda não existem consultas registradas.
            </div>
          )}
        </div>
      </section>

      <footer>
        <strong>AgroClima Inteligente</strong>
        <span>Integração de dados meteorológicos · 2026</span>
      </footer>
    </main>
  );
}

export default App;
