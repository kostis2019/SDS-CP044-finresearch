import gradio as gr
from agents.manager_agent import ManagerAgent

print("Creating ManagerAgent...")
manager = ManagerAgent()
print("Manager created!")

print("Creating Gradio interface...")
with gr.Blocks(title="Test") as app:
    gr.Markdown("# Test App")
    ticker_input = gr.Textbox(label="Ticker")
    output = gr.Textbox(label="Output")
    btn = gr.Button("Test")

    def test_fn(ticker):
        return f"Received: {ticker}"

    btn.click(test_fn, inputs=[ticker_input], outputs=[output])

print("Launching app...")
app.launch(server_port=7860)
