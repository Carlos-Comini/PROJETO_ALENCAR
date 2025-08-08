import streamlit as st
from datetime import datetime

def exibir():
	st.markdown("""
		<style>
		.dashboard-box {
			background: #222a35;
			border-radius: 16px;
			padding: 32px;
			margin-bottom: 32px;
			box-shadow: 0 4px 24px #0003;
			color: #fff;
		}
		.dashboard-title {
			font-size: 2.2rem;
			font-weight: 700;
			color: #42a5f5;
			margin-bottom: 16px;
		}
		.dashboard-sub {
			font-size: 1.2rem;
			color: #b0b8c1;
			margin-bottom: 32px;
		}
		.dashboard-grid {
			display: flex;
			gap: 32px;
			flex-wrap: wrap;
		}
		.dashboard-card {
			background: #263a53;
			border-radius: 12px;
			padding: 24px;
			min-width: 220px;
			flex: 1;
			box-shadow: 0 2px 8px #0002;
			color: #fff;
		}
		.dashboard-card-title {
			font-size: 1.1rem;
			font-weight: 600;
			margin-bottom: 8px;
			color: #42a5f5;
		}
		.dashboard-card-value {
			font-size: 2rem;
			font-weight: 700;
		}
		</style>
	""", unsafe_allow_html=True)

	st.markdown('<div class="dashboard-box">', unsafe_allow_html=True)
	st.markdown('<div class="dashboard-title">Bem-vindo ao Painel Alencar</div>', unsafe_allow_html=True)
	st.markdown('<div class="dashboard-sub">Resumo das principais funcionalidades do sistema</div>', unsafe_allow_html=True)

	# Cards de resumo (exemplo)
	st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
	st.markdown('''
		<div class="dashboard-card">
			<div class="dashboard-card-title">Empresas Cadastradas</div>
			<div class="dashboard-card-value">{empresas}</div>
		</div>
		<div class="dashboard-card">
			<div class="dashboard-card-title">Usuários</div>
			<div class="dashboard-card-value">{usuarios}</div>
		</div>
		<div class="dashboard-card">
			<div class="dashboard-card-title">Arquivos Contábeis</div>
			<div class="dashboard-card-value">{arquivos}</div>
		</div>
		<div class="dashboard-card">
			<div class="dashboard-card-title">XMLs Recebidos</div>
			<div class="dashboard-card-value">{xmls}</div>
		</div>
	'''.format(
		empresas=_contar_empresas(),
		usuarios=_contar_usuarios(),
		arquivos=_contar_arquivos(),
		xmls=_contar_xmls()
	), unsafe_allow_html=True)
	st.markdown('</div>', unsafe_allow_html=True)
	st.markdown('</div>', unsafe_allow_html=True)

	st.markdown("""
		<div style='margin-top:32px; color:#b0b8c1;'>
			Última atualização: {data}
		</div>
	""".format(data=datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)

def _contar_empresas():
	try:
		from funcoes_compartilhadas.empresas_sql import listar_empresas
		return len(listar_empresas())
	except:
		return "—"

def _contar_usuarios():
	try:
		from funcoes_compartilhadas.usuarios_sql import listar_usuarios
		return len(listar_usuarios())
	except:
		return "—"

def _contar_arquivos():
	try:
		from funcoes_compartilhadas.documentos_sql import listar_documentos
		return len([d for d in listar_documentos() if not d["nome"].lower().endswith(".xml")])
	except:
		return "—"

def _contar_xmls():
	try:
		from funcoes_compartilhadas.documentos_sql import listar_documentos
		return len([d for d in listar_documentos() if d["nome"].lower().endswith(".xml")])
	except:
		return "—"

