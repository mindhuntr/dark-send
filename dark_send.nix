{ config, pkgs, ... }:

let
  dark-send = pkgs.callPackage ./default.nix { };
in
{
  home.packages = [ dark-send ];

  systemd.user.services.dark-send = {
    Unit = {
      Description = "dark-send Telegram daemon";
      After = [ "network.target" ];
    };
    Service = {
      Type = "simple";
      ExecStart = "${dark-send}/bin/dark-send-daemon";
      Restart = "on-failure";
      RestartSec = 5;
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
