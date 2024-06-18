from pathlib import Path
import gradio as gr

from resq.app.functional import *


def app(
    server_ip="0.0.0.0",
    server_port=7860,
    public=False,
    logs_path="./logs",
):
    """Defines the frontend and backend of the Gradio application"""

    ##########################################################
    ######################  Frontend #########################
    ##########################################################

    js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """

    app = gr.Blocks(js=js_func, analytics_enabled=False)

    with app:
        gr.Markdown(
            """
                <div style="text-align:center;">
                    <span style="font-size:3em; font-weight:bold; color:rgb(93, 134, 180);">SQL Query Interface</span>
                </div>
                <div style="text-align:center;">
                    <span style="font-size:1em; color:rgb(208, 215, 226);">Enter a natural language query to retrieve data from the database</span>
                </div>
                """
        )
        # ==================================================================
        # Create the gradio objects

        llm_gradio = gr.State(None)
        database_gradio = gr.State(None)

        logs_path = gr.State(logs_path)
        query = gr.State(None)
        output_dataframe = gr.State(None)
        output_text = gr.State(None)
        log_panel = gr.State(None)

        # ==============================================================

        with gr.Tab(label="Chat"):

            gr.Image(
                str(
                    Path.joinpath(
                        Path(__file__).parent.parent.parent, r"img/Real-Estate.jpg"
                    )
                ),
                height=480,
                label="Your Image",
                show_download_button=False,
                show_label=False,
            )
            query = gr.Textbox(
                lines=2, placeholder="Enter your query here...", label="Chat"
            )
            output_dataframe = gr.Dataframe(label="Query Results")
            output_text = gr.Textbox(
                lines=2, placeholder="Output text...", label="Text Output"
            )
            submit_button = gr.Button("Submit")

        # ==================================================

        with gr.Tab("Logging"):
            # log_panel = gr.Code(label="Logs", language="shell", interactive=False, lines=40)
            log_panel = gr.Textbox(
                label="Logs", interactive=False, lines=40, max_lines=100
            )

        # ==============================================================

        ##########################################################
        ######################  back-end #########################
        ##########################################################

        submit_button.click(
            fn=process_chat,
            inputs=[llm_gradio, database_gradio, query],
            outputs=[output_dataframe, output_text, llm_gradio, database_gradio],
            queue=False,
        )

        # For this function to run on a separate thread, it needs to be a generator,
        # queues and concurrency need to be enabled
        app.load(
            fn=extract_log_data,
            inputs=[logs_path],
            outputs=[log_panel],
            every=2,
            scroll_to_output=True,
        )

    app.queue().launch(
        debug=True,
        server_name=server_ip,
        server_port=server_port,
        auth=authenticate,
        share=public,
        # max_threads=1
    )


# ==============================================================================
