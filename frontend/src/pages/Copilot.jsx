import Chatbot from "../components/Chatbot";

export default function Copilot() {
  return (
    <div className="h-[calc(100vh-64px)] p-4">
      <Chatbot symbols={["AAPL", "TSLA"]} />
    </div>
  );
}
