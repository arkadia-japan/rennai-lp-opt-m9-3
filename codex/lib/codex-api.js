const { Configuration, OpenAIApi } = require('openai');
const fs = require('fs-extra');
const path = require('path');

class CodexAPI {
  constructor() {
    this.config = null;
    this.openai = null;
    this.loadConfig();
  }

  async loadConfig() {
    try {
      // 環境変数から設定を読み込み
      require('dotenv').config();
      
      // 設定ファイルから設定を読み込み
      const configPath = path.join(process.cwd(), '.codex-config.json');
      if (await fs.pathExists(configPath)) {
        this.config = await fs.readJson(configPath);
      } else {
        throw new Error('設定ファイルが見つかりません。codex-cli init を実行してください。');
      }

      // OpenAI APIを初期化
      const configuration = new Configuration({
        apiKey: process.env.OPENAI_API_KEY,
      });
      this.openai = new OpenAIApi(configuration);
    } catch (error) {
      console.error('設定の読み込みに失敗しました:', error.message);
    }
  }

  async generateCode(prompt, language = 'javascript', options = {}) {
    try {
      if (!this.openai) {
        throw new Error('OpenAI APIが初期化されていません');
      }

      const systemPrompt = this.buildSystemPrompt(language);
      const userPrompt = this.buildUserPrompt(prompt, language);

      const response = await this.openai.createChatCompletion({
        model: this.config.model || 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        max_tokens: options.maxTokens || this.config.maxTokens || 2048,
        temperature: options.temperature || this.config.temperature || 0.1,
        top_p: options.topP || this.config.topP || 1.0,
        frequency_penalty: options.frequencyPenalty || this.config.frequencyPenalty || 0.0,
        presence_penalty: options.presencePenalty || this.config.presencePenalty || 0.0,
      });

      return this.extractCodeFromResponse(response.data.choices[0].message.content, language);
    } catch (error) {
      console.error('コード生成エラー:', error.message);
      throw error;
    }
  }

  async explainCode(code, language = 'javascript') {
    try {
      const prompt = `以下の${language}コードを日本語で詳しく説明してください：\n\n${code}`;
      
      const response = await this.openai.createChatCompletion({
        model: this.config.model || 'gpt-4',
        messages: [
          { role: 'system', content: 'あなたは優秀なプログラミング講師です。コードを分かりやすく日本語で説明してください。' },
          { role: 'user', content: prompt }
        ],
        max_tokens: this.config.maxTokens || 2048,
        temperature: 0.3,
      });

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('コード説明エラー:', error.message);
      throw error;
    }
  }

  async refactorCode(code, language = 'javascript', instructions = '') {
    try {
      const prompt = `以下の${language}コードをリファクタリングしてください。${instructions}\n\nコード：\n${code}`;
      
      const response = await this.openai.createChatCompletion({
        model: this.config.model || 'gpt-4',
        messages: [
          { role: 'system', content: 'あなたは優秀なソフトウェアエンジニアです。コードの可読性、パフォーマンス、保守性を向上させるリファクタリングを行ってください。' },
          { role: 'user', content: prompt }
        ],
        max_tokens: this.config.maxTokens || 2048,
        temperature: 0.1,
      });

      return this.extractCodeFromResponse(response.data.choices[0].message.content, language);
    } catch (error) {
      console.error('リファクタリングエラー:', error.message);
      throw error;
    }
  }

  async fixBugs(code, language = 'javascript', errorMessage = '') {
    try {
      const prompt = `以下の${language}コードのバグを修正してください。${errorMessage ? `エラーメッセージ: ${errorMessage}` : ''}\n\nコード：\n${code}`;
      
      const response = await this.openai.createChatCompletion({
        model: this.config.model || 'gpt-4',
        messages: [
          { role: 'system', content: 'あなたは優秀なデバッガーです。コードのバグを特定し、修正してください。' },
          { role: 'user', content: prompt }
        ],
        max_tokens: this.config.maxTokens || 2048,
        temperature: 0.1,
      });

      return this.extractCodeFromResponse(response.data.choices[0].message.content, language);
    } catch (error) {
      console.error('バグ修正エラー:', error.message);
      throw error;
    }
  }

  buildSystemPrompt(language) {
    const languageMap = {
      javascript: 'JavaScript',
      typescript: 'TypeScript',
      python: 'Python',
      java: 'Java',
      csharp: 'C#',
      cpp: 'C++',
      go: 'Go',
      rust: 'Rust',
      php: 'PHP',
      ruby: 'Ruby'
    };

    const langName = languageMap[language] || language;
    
    return `あなたは優秀な${langName}プログラマーです。
高品質で読みやすく、保守性の高いコードを生成してください。
以下の点に注意してください：
- 適切なコメントを含める
- ベストプラクティスに従う
- エラーハンドリングを含める
- 可読性を重視する
- パフォーマンスを考慮する`;
  }

  buildUserPrompt(prompt, language) {
    const template = this.config.prompts?.codeGeneration || 'Generate {language} code for: {description}';
    return template
      .replace('{language}', language)
      .replace('{description}', prompt);
  }

  extractCodeFromResponse(response, language) {
    // コードブロックを抽出
    const codeBlockRegex = new RegExp(`\`\`\`(?:${language})?\\s*([\\s\\S]*?)\`\`\``, 'gi');
    const matches = response.match(codeBlockRegex);
    
    if (matches && matches.length > 0) {
      // 最初のコードブロックを返す
      return matches[0]
        .replace(/```[\w]*\s*/, '')
        .replace(/```\s*$/, '')
        .trim();
    }
    
    // コードブロックが見つからない場合は、レスポンス全体を返す
    return response.trim();
  }

  async saveCode(code, filePath, language) {
    try {
      // ディレクトリが存在しない場合は作成
      await fs.ensureDir(path.dirname(filePath));
      
      // 言語に応じたテンプレートを追加
      const template = this.config.languages?.[language]?.template || '';
      const finalCode = template + code;
      
      // ファイルに保存
      await fs.writeFile(filePath, finalCode, 'utf8');
      
      return filePath;
    } catch (error) {
      console.error('ファイル保存エラー:', error.message);
      throw error;
    }
  }
}

module.exports = CodexAPI;
