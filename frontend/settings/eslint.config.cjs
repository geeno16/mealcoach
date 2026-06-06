// @ts-check

const js = require("@eslint/js");
const importPlugin = require("eslint-plugin-import-x");
const prettierRecommended = require("eslint-plugin-prettier/recommended");
const reactPlugin = require("eslint-plugin-react");
const reactHooksPlugin = require("eslint-plugin-react-hooks");
const globals = require("globals");
const tseslint = require("typescript-eslint");

const noUnusedVarsOptions = {
  args: "after-used",
  vars: "all",
  ignoreRestSiblings: true,
  varsIgnorePattern: "^_",
  argsIgnorePattern: "^_",
  destructuredArrayIgnorePattern: "^_",
};

/** @type {import("eslint").Linter.Config[]} */
const config = [
  {
    ignores: ["dist/", "node_modules/"],
  },

  js.configs.recommended,
  ...tseslint.configs.recommended,

  {
    rules: {
      "@typescript-eslint/no-require-imports": "off",
      "@typescript-eslint/no-unused-vars": "off",
      eqeqeq: "error",
      "no-unused-vars": ["error", noUnusedVarsOptions],
      "no-useless-escape": "warn",
    },
  },

  prettierRecommended,
  {
    rules: {
      "prettier/prettier": "warn",
    },
  },

  reactPlugin.configs.flat.recommended,
  reactPlugin.configs.flat["jsx-runtime"],
  reactHooksPlugin.configs["recommended-latest"],
  {
    rules: {
      "react/prop-types": "off",
      "react/jsx-no-target-blank": "off",
      "react/display-name": "warn",
    },
    settings: {
      react: { version: "detect" },
    },
  },

  {
    files: ["**/*.cjs"],
    languageOptions: {
      globals: { ...globals.node },
    },
  },

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      globals: { ...globals.browser },
      parser: tseslint.parser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        ecmaVersion: 2022,
      },
    },
    plugins: {
      "@typescript-eslint": tseslint.plugin,
    },
    rules: {
      "@typescript-eslint/consistent-type-imports": ["warn", { fixStyle: "inline-type-imports" }],
      "no-unused-vars": "off",
      "no-use-before-define": "off",
      "@typescript-eslint/no-use-before-define": "warn",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": ["error", noUnusedVarsOptions],
    },
  },

  importPlugin.flatConfigs.recommended,
  importPlugin.flatConfigs.typescript,
  {
    rules: {
      "sort-imports": "off",
      "import-x/no-duplicates": "warn",
      "import-x/consistent-type-specifier-style": ["warn", "prefer-inline"],
      "import-x/first": "warn",
      "import-x/newline-after-import": "warn",
      "import-x/no-unresolved": "off",
      "import-x/order": [
        "warn",
        {
          groups: [
            "builtin",
            "external",
            "internal",
            "parent",
            "sibling",
            "index",
          ],
          alphabetize: { order: "asc", orderImportKind: "ignore" },
          "newlines-between": "always",
          distinctGroup: false,
          pathGroupsExcludedImportTypes: ["builtin"],
        },
      ],
    },
    settings: {
      "import-x/parsers": {
        "@typescript-eslint/parser": [".ts", ".tsx"],
      },
      "import-x/resolver": {
        typescript: { alwaysTryTypes: true },
      },
    },
  },
];

module.exports = config;
