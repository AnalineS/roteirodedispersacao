const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Chaves da API OpenRouter
const OPENROUTER_API_KEY_LLAMA = "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";
const OPENROUTER_API_KEY_QWEN = "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";
const OPENROUTER_API_KEY_GEMINI = "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";

const LLAMA3_MODEL = "meta-llama/llama-3.3-70b-instruct:free";
const QWEN_MODEL = "qwen/qwen3-14b:free";
const GEMINI_MODEL = "google/gemini-2.0-flash-exp:free";

// Templates de linguagem natural
const NATURAL_TEMPLATES = {
    "dr_gasnelio": {
        "greeting": [
            "Saudações! Sou o Dr. Gasnelio. Minha pesquisa foca no roteiro de dispensação para a prática da farmácia clínica. Como posso auxiliá-lo hoje?",
            "Olá! Aqui é o Dr. Gasnelio. Tenho dedicado minha carreira ao estudo da dispensação farmacêutica. Em que posso ajudá-lo?",
            "Bem-vindo! Sou o Dr. Gasnelio, especialista em farmácia clínica. Como posso contribuir com sua consulta hoje?"
        ],
        "thinking": [
            "Deixe-me analisar essa questão com base na minha pesquisa...",
            "Interessante pergunta. Vou consultar os dados da tese...",
            "Essa é uma questão importante. Permita-me buscar nas fontes..."
        ],
        "confidence_high": [
            "Baseado na minha pesquisa, posso afirmar com confiança que:",
            "Os dados da tese são bastante claros sobre isso:",
            "Minha análise da literatura confirma que:"
        ],
        "confidence_medium": [
            "Com base no que encontrei na tese, posso sugerir que:",
            "Os dados disponíveis indicam que:",
            "Baseado na pesquisa, parece que:"
        ],
        "confidence_low": [
            "Essa questão é interessante, mas não encontrei dados específicos na tese. Sugiro consultar:",
            "Não tenho informações detalhadas sobre isso na pesquisa, mas posso orientar para:",
            "Essa área não foi coberta especificamente na tese, mas posso sugerir:"
        ]
    },
    "ga": {
        "greeting": [
            "Opa, tudo certo? Aqui é o Gá! Tô aqui pra gente desenrolar qualquer dúvida sobre o uso correto de medicamentos e o roteiro de dispensação. Manda a ver!",
            "E aí, beleza? Sou o Gá! Tô aqui pra te ajudar com qualquer parada sobre remédios e farmácia. Fala aí!",
            "Oi! Aqui é o Gá! Tô aqui pra gente conversar sobre medicamentos e como usar direitinho. Qual é a boa?"
        ],
        "thinking": [
            "Deixa eu dar uma olhada na tese aqui...",
            "Hmm, deixa eu ver o que tem sobre isso...",
            "Vou procurar essa informação pra você..."
        ],
        "confidence_high": [
            "Olha só, encontrei isso na tese:",
            "Tá aqui, direto da pesquisa:",
            "Dá uma olhada nisso que achei:"
        ],
        "confidence_medium": [
            "Olha, pelo que vi na tese:",
            "Acho que é mais ou menos assim:",
            "Pelo que entendi da pesquisa:"
        ],
        "confidence_low": [
            "Ih, essa eu não sei certinho, mas posso te ajudar a procurar!",
            "Não achei essa informação específica, mas posso te orientar!",
            "Essa parte não tá muito clara na tese, mas vamos ver o que tem!"
        ]
    }
};

// Carregar texto da tese
let mdText = "";
try {
    const mdPath = path.join(__dirname, '../PDFs/Roteiro de Dsispensação - Hanseníase.md');
    mdText = fs.readFileSync(mdPath, 'utf8');
} catch (error) {
    console.error('Erro ao carregar arquivo Markdown:', error);
    mdText = "Erro ao carregar o documento da tese.";
}

// Funções auxiliares
function getRandomPhrase(templates) {
    if (templates && templates.length > 0) {
        return templates[Math.floor(Math.random() * templates.length)];
    }
    return "";
}

function getNaturalPhrase(persona, category, confidenceLevel = "medium") {
    const templates = NATURAL_TEMPLATES[persona] || {};
    let categoryTemplates = templates[category] || [];
    
    if (category === "confidence") {
        const confidenceKey = `confidence_${confidenceLevel}`;
        categoryTemplates = templates[confidenceKey] || [];
    }
    
    return getRandomPhrase(categoryTemplates);
}

function findRelevantContext(question, fullText, maxLength = 800) {
    // Busca simples por palavras-chave
    const questionWords = question.toLowerCase().match(/\w+/g) || [];
    const textWords = fullText.toLowerCase().match(/\w+/g) || [];
    
    // Encontrar seções com mais palavras em comum
    const sections = fullText.split('\n\n');
    let bestSection = sections[0] || "";
    let bestScore = 0;
    
    for (const section of sections) {
        const sectionWords = section.toLowerCase().match(/\w+/g) || [];
        const commonWords = questionWords.filter(word => sectionWords.includes(word));
        const score = commonWords.length / questionWords.length;
        
        if (score > bestScore) {
            bestScore = score;
            bestSection = section;
        }
    }
    
    return bestSection.substring(0, maxLength);
}

function transformForGa(text) {
    // Transformar texto formal em informal
    const transformations = {
        'medicamento': 'remédio',
        'farmacêutico': 'farmacêutico',
        'dispensação': 'dispensação',
        'prescrição': 'receita',
        'posologia': 'como usar',
        'administração': 'como tomar',
        'contraindicação': 'quando não usar',
        'interação': 'mistura com outros remédios',
        'adverso': 'efeito ruim',
        'reação': 'reação',
        'tratamento': 'tratamento',
        'terapia': 'tratamento',
        'protocolo': 'jeito de fazer',
        'metodologia': 'método',
        'análise': 'análise',
        'estudo': 'estudo',
        'pesquisa': 'pesquisa',
        'investigação': 'investigação',
        'observação': 'observação',
        'monitoramento': 'acompanhamento',
        'acompanhamento': 'acompanhamento',
        'seguimento': 'seguimento',
        'avaliação': 'avaliação',
        'exame': 'exame',
        'teste': 'teste',
        'diagnóstico': 'diagnóstico',
        'sintoma': 'sintoma',
        'sinal': 'sinal',
        'manifestação': 'manifestação',
        'apresentação': 'apresentação',
        'característica': 'característica',
        'propriedade': 'propriedade',
        'qualidade': 'qualidade',
        'atributo': 'atributo',
        'aspecto': 'aspecto',
        'fator': 'fator',
        'elemento': 'elemento',
        'componente': 'componente',
        'constituinte': 'constituinte',
        'ingrediente': 'ingrediente',
        'substância': 'substância',
        'composição': 'composição',
        'formulação': 'formulação',
        'preparação': 'preparação',
        'elaboração': 'elaboração',
        'desenvolvimento': 'desenvolvimento',
        'implementação': 'implementação',
        'aplicação': 'aplicação',
        'utilização': 'uso',
        'emprego': 'uso',
        'consumo': 'consumo',
        'ingestão': 'tomar',
        'administração oral': 'tomar pela boca',
        'via oral': 'pela boca',
        'via parenteral': 'injeção',
        'intramuscular': 'no músculo',
        'intravenosa': 'na veia',
        'subcutânea': 'debaixo da pele',
        'tópica': 'na pele',
        'local': 'local',
        'sistêmica': 'no corpo todo',
        'absorção': 'absorção',
        'distribuição': 'distribuição',
        'metabolismo': 'metabolismo',
        'eliminação': 'eliminação',
        'excreção': 'excreção',
        'meia-vida': 'meia-vida',
        'biodisponibilidade': 'biodisponibilidade',
        'concentração': 'concentração',
        'dosagem': 'dosagem',
        'dose': 'dose',
        'quantidade': 'quantidade',
        'volume': 'volume',
        'peso': 'peso',
        'massa': 'massa',
        'frequência': 'frequência',
        'intervalo': 'intervalo',
        'duração': 'duração',
        'período': 'período',
        'ciclo': 'ciclo',
        'sessão': 'sessão',
        'aplicação': 'aplicação',
        'administração': 'administração'
    };
    
    let transformedText = text;
    for (const [formal, informal] of Object.entries(transformations)) {
        const regex = new RegExp(`\\b${formal}\\b`, 'gi');
        transformedText = transformedText.replace(regex, informal);
    }
    
    return transformedText;
}

async function callOpenRouterModel(question, context, persona, model, apiKey) {
    try {
        const systemPrompt = persona === "dr_gasnelio" 
            ? "Você é o Dr. Gasnelio, especialista em farmácia clínica. Responda de forma acadêmica e formal, baseando-se na tese sobre roteiro de dispensação para hanseníase."
            : "Você é o Gá, um farmacêutico descontraído. Responda de forma informal e amigável, explicando sobre medicamentos e farmácia de forma simples.";

        const userPrompt = `Contexto da tese: ${context}\n\nPergunta: ${question}\n\nResponda baseando-se no contexto fornecido.`;

        const response = await axios.post('https://openrouter.ai/api/v1/chat/completions', {
            model: model,
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userPrompt }
            ],
            temperature: 0.7,
            max_tokens: 500
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });

        return response.data.choices[0].message.content;
    } catch (error) {
        console.error('Erro ao chamar OpenRouter:', error);
        return null;
    }
}

async function callChatbotWithFallback(question, context, persona) {
    // Tentar diferentes modelos em ordem
    const models = [
        { model: LLAMA3_MODEL, apiKey: OPENROUTER_API_KEY_LLAMA },
        { model: QWEN_MODEL, apiKey: OPENROUTER_API_KEY_QWEN },
        { model: GEMINI_MODEL, apiKey: OPENROUTER_API_KEY_GEMINI }
    ];

    for (const { model, apiKey } of models) {
        try {
            const response = await callOpenRouterModel(question, context, persona, model, apiKey);
            if (response) {
                return response;
            }
        } catch (error) {
            console.error(`Erro com modelo ${model}:`, error);
            continue;
        }
    }

    // Fallback se todos os modelos falharem
    return persona === "ga" 
        ? "Ih, deu ruim aqui! Mas olha, pelo que vi na tese, isso tem a ver com medicamentos e tal. Tenta perguntar de outro jeito ou me fala mais sobre o que você quer saber!"
        : "Peço desculpas, mas estou enfrentando dificuldades técnicas no momento. Com base na minha pesquisa sobre dispensação farmacêutica, posso orientá-lo sobre o uso correto de medicamentos. Poderia reformular sua pergunta?";
}

async function answerQuestion(question, persona, conversationHistory = []) {
    try {
        // Encontrar contexto relevante
        const context = findRelevantContext(question, mdText);
        
        // Chamar chatbot
        const response = await callChatbotWithFallback(question, context, persona);
        
        // Formatar resposta baseada na persona
        let formattedResponse = response;
        if (persona === "ga") {
            formattedResponse = transformForGa(response);
        }
        
        return {
            answer: formattedResponse,
            context: context.substring(0, 200) + "...",
            confidence: "high",
            persona: persona
        };
    } catch (error) {
        console.error('Erro ao processar pergunta:', error);
        return {
            answer: persona === "ga" 
                ? "Ih, deu ruim aqui! Tenta de novo ou me fala de outro jeito!"
                : "Peço desculpas, mas ocorreu um erro técnico. Poderia tentar novamente?",
            context: "",
            confidence: "low",
            persona: persona
        };
    }
}

// Handler principal da função serverless
exports.handler = async (event, context) => {
    // Configurar CORS
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    // Responder a requisições OPTIONS (preflight)
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        if (event.httpMethod === 'POST') {
            const body = JSON.parse(event.body);
            const { question, persona = "dr_gasnelio", conversation_history = [] } = body;

            if (!question) {
                return {
                    statusCode: 400,
                    headers,
                    body: JSON.stringify({ error: 'Pergunta é obrigatória' })
                };
            }

            const result = await answerQuestion(question, persona, conversation_history);

            return {
                statusCode: 200,
                headers,
                body: JSON.stringify(result)
            };
        } else if (event.httpMethod === 'GET') {
            // Health check
            if (event.path.endsWith('/health')) {
                return {
                    statusCode: 200,
                    headers,
                    body: JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() })
                };
            }
            
            // Info endpoint
            if (event.path.endsWith('/info')) {
                return {
                    statusCode: 200,
                    headers,
                    body: JSON.stringify({
                        name: 'Chatbot Roteiro de Dispensação',
                        version: '2.0',
                        personas: ['dr_gasnelio', 'ga'],
                        status: 'online'
                    })
                };
            }
        }

        return {
            statusCode: 404,
            headers,
            body: JSON.stringify({ error: 'Endpoint não encontrado' })
        };

    } catch (error) {
        console.error('Erro na função:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Erro interno do servidor' })
        };
    }
}; 