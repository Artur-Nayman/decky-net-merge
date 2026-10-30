# Net Merge for Decky

A [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) plugin that runs
[net-merge](https://github.com/net-merge/net-merge) on the Steam Deck: Wi-Fi, USB Ethernet and
phone USB tethers are used at the same time, so Steam downloads (many connections) get the
bandwidth of every link added up.

One toggle in the Quick Access menu, plus live per-adapter speeds.

## You need a second connection

The Deck only has Wi-Fi built in. Add one of:

- a USB-C Ethernet adapter or dock with Ethernet
- an Android phone with USB tethering on

## Install

1. Download `decky-net-merge.zip` from the [latest release](https://github.com/Artur-Nayman/decky-net-merge/releases/latest).
2. Decky settings → Developer mode on → Developer → *Install plugin from ZIP*.

## Notes

- A single connection always uses one link. Steam, browsers and torrents open many, so they speed up.
- All traffic goes through a virtual adapter while it's on. Turn it off for latency-sensitive online games if you notice a difference.
- On load the plugin runs `net-merge cleanup` to remove routes left behind by a crash or hard power-off.
- Log: `~/homebrew/logs/decky-net-merge/net-merge.log`.

## Build

CI builds everything: net-merge (static Go binary, pinned by `NET_MERGE_VERSION` in
`.github/workflows/build.yml`) and the frontend, packaged as a Decky zip. Push a `v*` tag to
publish a release.

Locally: `pnpm install && pnpm build`, put a Linux amd64 `net-merge` binary in `bin/`.
Backend smoke test: `python3 tests/test_main.py`.

## License

BSD-3-Clause. The bundled net-merge binary is MIT (see `bin/net-merge.LICENSE`).
