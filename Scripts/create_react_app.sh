#!/bin/bash

function tailwind() {
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    echo -e "/** @type {import('tailwindcss').Config} */\n\
export default {\n\
content: [\n\
\"./index.html\",\n\
\"./src/**/*.{js,ts,jsx,tsx}\",\n\
],\n\
theme: {\n\
extend: {},\n\
},\n\
plugins: [],\n\
}" > tailwind.config.js
    echo -e "@tailwind base;\n\
@tailwind components;\n\
@tailwind utilities;" > src/index.css
    npm install --save prettier-plugin-tailwindcss
    echo -e "{
\"tabWidth\": 2,\n\
\"useTabs\": false,\n\
\"plugins\": [\"prettier-plugin-tailwindcss\"]\n\
}" > .prettierrc
}

function config() {
    echo "" > src/index.css
    echo -e "import ReactDOM from \"react-dom/client\";\n\
import App from \"./App.tsx\";\n\
import \"./index.css\";\n\
\n\
ReactDOM.createRoot(document.getElementById(\"root\")!).render(<App />);" > src/main.tsx
    echo -e "export default function App() {\n\
return <></>;\n\
}\n\
" > src/App.tsx
    rm -rf src/App.css
    rm -rf src/assets
    rm -rf public
}

function signals() {
    npm install @preact/signals-react
}

function recoil() {
    npm install recoil
    echo -e "import ReactDOM from \"react-dom/client\";\n\
import { RecoilRoot } from \"recoil\";\n\
import App from \"./App.tsx\";\n\
import \"./index.css\";\n\
\n\
ReactDOM.createRoot(document.getElementById(\"root\")!).render(\n\
<RecoilRoot>\n\
<App />\n\
</RecoilRoot>\n\
);" > src/main.tsx
}


echo "What name do you want to give to your app?"
echo -n "> "
read REPLY
if [ -z "$REPLY" ]; then
    echo "Error: you must provide a name"
    exit 1
fi
npm create vite@latest $REPLY -- --template react-ts
cd $REPLY
npm install --save prettier
config
echo "Do you want to install TailwindCSS?"
echo "[ y ] Yes"
echo "[ * ] No"
echo -n "> "
read REPLY
if [ "$REPLY" = "y" ]; then
    tailwind
fi
echo "Which state management do you want to use?"
echo "[ 1 ] Recoil"
echo "[ 2 ] Signals"
echo "[ * ]  None"
echo -n "> "
read REPLY
if [ "$REPLY" = "1" ]; then
    recoil
elif [ "$REPLY" = "2" ]; then
    signals
fi
pnpm install
code .