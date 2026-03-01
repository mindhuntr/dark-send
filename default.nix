{
  lib,
  python3,
  fetchFromGitHub,
}:

python3.pkgs.buildPythonApplication rec {
  pname = "dark-send";
  version = "1.2.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "mindhuntr";
    repo = "dark-send";
    rev = "v${version}";
    hash = "sha256-2fzAFI3j1hklhzO/aHHf0h7KV761vTg+Oo2zRUgL5Co=";
  };

  build-system = [
    python3.pkgs.setuptools
    python3.pkgs.wheel
  ];

  dependencies = with python3.pkgs; [
    hachoir
    inquirerpy
    telethon
    tqdm
  ];

  pythonImportsCheck = [
    "dark_send"
  ];

  postFixup = ''
    cp $out/bin/.dark-send-wrapped $out/bin/dark-send-daemon
    substituteInPlace $out/bin/dark-send-daemon \
    --replace "from dark_send.cli import entrypoint" "from dark_send.daemon import main" \
    --replace "entrypoint()" "main()"
  '';

  meta = {
    description = "A Command Line Interface for Telegram";
    homepage = "https://github.com/mindhuntr/dark-send";
    license = lib.licenses.gpl3Only;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "dark-send";
  };
}
