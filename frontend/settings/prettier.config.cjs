/** @type {import("prettier").Options} */
const config = {
  trailingComma: "all",
  tabWidth: 2,
  quoteProps: "preserve",
  semi: true,
  proseWrap: "always",
  plugins: ["prettier-plugin-css-order"],
  cssDeclarationSorterKeepOverrides: false,
};

module.exports = config;
