#!/usr/bin/env node

const { Command } = require('commander');
const chalk = require('chalk');
const inquirer = require('inquirer');
const fs = require('fs-extra');
const path = require('path');
require('dotenv').config();

const program = new Command();

// Codex CLI設定
program
  .name('codex-cli')
  .description('Codex CLI for Windsurf IDE')
  .version('1.0.0');

// 初期化コマンド
program
  .command('init')
  .description('Initialize Codex CLI configuration')
  .action(async () => {
    console.log(chalk.blue('🚀 Codex CLI初期化を開始します...'));
    
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'apiKey',
        message: 'OpenAI API Keyを入力してください:',
        validate: (input) => input.length > 0 || 'API Keyは必須です'
      },
      {
        type: 'list',
        name: 'model',
        message: '使用するモデルを選択してください:',
        choices: ['gpt-4', 'gpt-3.5-turbo', 'codex-davinci-002'],
        default: 'gpt-4'
      },
      {
        type: 'input',
        name: 'maxTokens',
        message: '最大トークン数を設定してください:',
        default: '2048',
        validate: (input) => !isNaN(input) || '数値を入力してください'
      }
    ]);

    // .envファイルを作成
    const envContent = `OPENAI_API_KEY=${answers.apiKey}
CODEX_MODEL=${answers.model}
MAX_TOKENS=${answers.maxTokens}
`;

    await fs.writeFile('.env', envContent);
    
    // 設定ファイルを作成
    const config = {
      model: answers.model,
      maxTokens: parseInt(answers.maxTokens),
      temperature: 0.1,
      outputDir: './output',
      windsurf: {
        integration: true,
        autoSave: true,
        formatOnSave: true
      }
    };

    await fs.writeJson('.codex-config.json', config, { spaces: 2 });
    
    console.log(chalk.green('✅ Codex CLI設定が完了しました！'));
    console.log(chalk.yellow('📁 設定ファイル: .codex-config.json'));
    console.log(chalk.yellow('🔐 環境変数: .env'));
  });

// コード生成コマンド
program
  .command('generate')
  .alias('gen')
  .description('Generate code using Codex')
  .option('-p, --prompt <prompt>', 'Code generation prompt')
  .option('-f, --file <file>', 'Output file path')
  .option('-l, --language <language>', 'Programming language', 'javascript')
  .action(async (options) => {
    try {
      console.log(chalk.blue('🤖 Codexでコード生成中...'));
      
      let prompt = options.prompt;
      if (!prompt) {
        const answer = await inquirer.prompt([
          {
            type: 'input',
            name: 'prompt',
            message: 'コード生成のプロンプトを入力してください:'
          }
        ]);
        prompt = answer.prompt;
      }

      // ここでCodex APIを呼び出す（実装例）
      const generatedCode = await generateCodeWithCodex(prompt, options.language);
      
      if (options.file) {
        await fs.ensureDir(path.dirname(options.file));
        await fs.writeFile(options.file, generatedCode);
        console.log(chalk.green(`✅ コードが ${options.file} に保存されました`));
      } else {
        console.log(chalk.cyan('生成されたコード:'));
        console.log(generatedCode);
      }
    } catch (error) {
      console.error(chalk.red('❌ エラー:'), error.message);
    }
  });

// Windsurf統合コマンド
program
  .command('windsurf')
  .description('Windsurf IDE integration commands')
  .option('--setup', 'Setup Windsurf integration')
  .option('--status', 'Check integration status')
  .action(async (options) => {
    if (options.setup) {
      console.log(chalk.blue('🔧 Windsurf統合をセットアップ中...'));
      await setupWindsurfIntegration();
      console.log(chalk.green('✅ Windsurf統合が完了しました！'));
    } else if (options.status) {
      await checkWindsurfStatus();
    } else {
      console.log(chalk.yellow('使用方法: codex-cli windsurf --setup または --status'));
    }
  });

// Codex API呼び出し関数（プレースホルダー）
async function generateCodeWithCodex(prompt, language) {
  // 実際のCodex API実装をここに追加
  return `// Generated ${language} code for: ${prompt}
// This is a placeholder implementation
console.log("Hello from Codex CLI!");
`;
}

// Windsurf統合セットアップ
async function setupWindsurfIntegration() {
  const windsurfConfig = {
    "codex-cli": {
      "enabled": true,
      "commands": {
        "generate": "codex-cli generate",
        "init": "codex-cli init"
      },
      "shortcuts": {
        "ctrl+shift+g": "codex-cli generate",
        "ctrl+shift+i": "codex-cli init"
      }
    }
  };

  await fs.writeJson('.windsurf/codex-integration.json', windsurfConfig, { spaces: 2 });
}

// Windsurf統合状態確認
async function checkWindsurfStatus() {
  const configExists = await fs.pathExists('.windsurf/codex-integration.json');
  const envExists = await fs.pathExists('.env');
  
  console.log(chalk.blue('📊 Windsurf統合状態:'));
  console.log(`設定ファイル: ${configExists ? chalk.green('✅') : chalk.red('❌')}`);
  console.log(`環境変数: ${envExists ? chalk.green('✅') : chalk.red('❌')}`);
}

program.parse();
