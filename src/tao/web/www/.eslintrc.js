module.exports = {
  "parser": "babel-eslint",
  "parserOptions": {
    "sourceType": "module",
    "ecmaVersion": 7,
    "ecmaFeatures": {
      "jsx": true,
      "experimentalObjectRestSpread": true
    }
  },
  "env": {
    "browser": true,
    "node": true,
    "es6": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended"
  ],
  "plugins": [
    "import",
    "react"
  ],
  "globals": {
    "API_SERVER_PLACEHOLDER": true
  },
  "rules": {
    "no-unused-vars": "off",
    "no-console": "off",
    // 行尾必须加分号
    "semi": "off",
    // 文件末尾必须留空行
    "eol-last": "off",

    // React必须作为全局变量
    "react/react-in-jsx-scope": "off",
    // prop必须校验
    "react/prop-types": "off",
    "react/display-name": "off",
    "react/no-deprecated": "off",
  }
};