export default function App() {
  return (
    <iframe
      data-testid="lucidflex-frame"
      title="LucidFlex $50K Battle Pass"
      src={`/lucidflex-app.html?v=${Date.now()}`}
      style={{ position: "fixed", inset: 0, width: "100%", height: "100%", border: 0, background: "#0a0a0f" }}
    />
  );
}
