import { PanelSection, PanelSectionRow, ToggleField, Field, staticClasses } from "@decky/ui";
import { callable, definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { FaNetworkWired } from "react-icons/fa";

// Field names match net-merge's status.json (engine.SlotStats); rates are bytes/s.
type Nic = { Name: string; State: string; Present: boolean; LinkIn: number; LinkOut: number; Active: number };
type Status = { running: boolean; on: boolean; nics: Nic[]; error: string | null };

const start = callable<[], boolean>("start");
const stop = callable<[], boolean>("stop");
const getStatus = callable<[], Status>("status");

const mbit = (bps: number) => ((bps * 8) / 1e6).toFixed(1);

function Content() {
  const [st, setSt] = useState<Status | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let alive = true;
    const tick = () => getStatus().then((s) => alive && setSt(s));
    tick();
    const id = setInterval(tick, 1000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const toggle = async (v: boolean) => {
    setBusy(true);
    await (v ? start() : stop());
    setSt(await getStatus());
    setBusy(false);
  };

  const nics = st?.nics ?? [];
  const total = nics.reduce((a, n) => a + n.LinkIn, 0);

  return (
    <PanelSection>
      <PanelSectionRow>
        <ToggleField
          label="Merge connections"
          description={st?.running && !st.on ? "Starting…" : "Spreads new connections over every adapter"}
          checked={!!st?.running}
          disabled={busy || !st}
          onChange={toggle}
        />
      </PanelSectionRow>
      {st?.error && (
        <PanelSectionRow>
          <Field label="Stopped" description={st.error} />
        </PanelSectionRow>
      )}
      {st?.on && (
        <PanelSectionRow>
          <Field label="Total down" focusable>{mbit(total)} Mbit/s</Field>
        </PanelSectionRow>
      )}
      {nics.map((n) => (
        <PanelSectionRow key={n.Name}>
          <Field
            label={n.Name + (n.Present ? "" : " (gone)")}
            description={`${n.State} · ${n.Active} flows · up ${mbit(n.LinkOut)}`}
            focusable
          >
            {mbit(n.LinkIn)} Mbit/s
          </Field>
        </PanelSectionRow>
      ))}
      {st?.on && nics.length < 2 && (
        <PanelSectionRow>
          <Field description="Only one adapter found. Plug in USB Ethernet or USB-tether a phone to get a second link." />
        </PanelSectionRow>
      )}
    </PanelSection>
  );
}

export default definePlugin(() => ({
  name: "Net Merge",
  titleView: <div className={staticClasses.Title}>Net Merge</div>,
  content: <Content />,
  icon: <FaNetworkWired />,
}));
