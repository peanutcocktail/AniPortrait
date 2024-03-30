import gradio as gr
import subprocess
import yaml
import os
import cv2

def get_video_frame_count(video_path):
    if video_path is None:
        return None
    
    video = cv2.VideoCapture(video_path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video.release()
    return frame_count

def initialize_yaml(config_path):
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            if config is None:
                print("YAML file is empty or contains invalid content. Initializing...")
                config = {'test_cases': {}}
                with open(config_path, 'w') as outfile:
                    yaml.safe_dump(config, outfile)
            else:
                print("YAML file is valid.")
    except FileNotFoundError:
        print("YAML file not found. Creating a new one...")
        config = {'test_cases': {}}
        with open(config_path, 'w') as outfile:
            yaml.safe_dump(config, outfile)

def run_vid2vid(image_path, video_path, width, height, length, seed, cfg, steps):
    # Assuming the rest of the configuration remains constant
    config_path = './configs/prompts/animation_facereenac.yaml'
    
    # Ensure paths are strings
    image_path_str = str(image_path)
    video_path_str = str(video_path)
    
    # Load the existing configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # If the file is somehow still empty or invalid, initialize config
    if config is None:
        config = {'test_cases': {}}
    
    # Update the configuration using string paths
    config['test_cases'] = {image_path_str: [video_path_str]}
    
    # Save the updated configuration
    with open(config_path, 'w') as file:
        yaml.safe_dump(config, file, default_flow_style=False)

    # Construct the command with all the additional arguments
    command = [
        "python", "-m", "scripts.vid2vid_gr",
        "--config", config_path,
        "-W", str(width),
        "-H", str(height),
        # "-L", str(length),
        "--seed", str(seed),
        "--cfg", str(cfg),
        "--steps", str(steps)
    ]
    # Conditionally add the "-L" argument if a meaningful value is provided
    if length is not None:
        command.extend(["-L", str(length)])

    # Only add "--fps" argument if it is provided (not None)
    # if fps is not None:
    #     command.extend(["--fps", str(fps)])

    # Run the vid2vid script with the specified parameters
    subprocess.run(command)
    
    # Assuming the script saves its output to a known, fixed path
    output_file_path = "output/result/result.mp4"
    
    # Return this path for Gradio to display the video
    return output_file_path

with gr.Blocks(title="AniPortrait") as blocks_app:
    gr.Markdown("# Gradio UI for AniPortrait vid2vid")
    gr.Markdown("Audio-Driven Synthesis of Photorealistic Portrait Animation")
    gr.Markdown("Original Project: https://github.com/Zejun-Yang/AniPortrait")
    
    with gr.Row():
        image_input = gr.Image(type="filepath", label="Upload Image")
        video_input = gr.PlayableVideo(label="Upload Video")
        
    with gr.Row():
        width = gr.Slider(minimum=256, maximum=1024, step=8, value=512, label="Width (-W)")
        height = gr.Slider(minimum=256, maximum=1024, step=8, value=512, label="Height (-H)")
        
    with gr.Row():
        length = gr.Number(value=None, label="Length (-L)")
        seed = gr.Number(value=42, label="Seed (--seed)")
    video_input.change(get_video_frame_count, inputs=video_input, outputs=length)
    
    with gr.Row():
        cfg = gr.Slider(minimum=0.1, maximum=10.0, step=0.1, value=3.5, label="Cfg (--cfg)")
        steps = gr.Slider(minimum=1, maximum=100.0, step=1, value=25, label="Steps (--steps)")
        
    # with gr.Row():
    #     fps = gr.Number(label="FPS (--fps)")
        
    output_video = gr.PlayableVideo(label="Result")

    def process_and_display(image_path, video_path, width, height, length, seed, cfg, steps):
        return run_vid2vid(image_path, video_path, width, height, length, seed, cfg, steps)
    
    run_button = gr.Button("Run")
    run_button.click(
        process_and_display, 
        inputs=[image_input, video_input, width, height, length, seed, cfg, steps],
        outputs=output_video
    )

if __name__ == "__main__":
    blocks_app.launch(share=True)
 