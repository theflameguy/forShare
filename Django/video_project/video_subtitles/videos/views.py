from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.views.decorators.http import require_POST
from .models import Video, Subtitle
from django.db.models import Q
import re
import subprocess
import os
import json



def process_video(video):
    video_path = video.file.path
    
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found at {video_path}")

    try:
        res = subprocess.run(["ffmpeg/ffmpeg.exe",'-i', video_path],capture_output=True,text=True)
        stream_details = extract_stream_details(res.stderr)
        for stream in stream_details:
            if len(stream[1]) < 1:
                stream[1] = "Null"
            subtitle_path = f'{video_path+stream[1]}.vtt'
            if stream[2] == 'Subtitle':
                subprocess.run([
                    'ffmpeg/ffmpeg.exe', '-i'
                    , video_path, '-map', f'0:{stream[0]}'
                    , subtitle_path
                    ])
                if not os.path.isfile(subtitle_path):
                    raise FileNotFoundError(f"!subtitle file not created at {subtitle_path}")
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                Subtitle.objects.create(video=video, language=stream[1], content=content,file=subtitle_path)
                


    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        return

def extract_stream_details(file_str):
    # Read the entire content of the text file
    content = file_str
    
    # Find all occurrences of "Stream #" in the text
    streams = re.findall(r'Stream #.*?(?:\n|$)', content, re.DOTALL)
    
    # Initialize a list to hold the extracted details
    extracted_details = []
    
    for stream in streams:
        # Count occurrences of ":" and extract the required part
        colon_count = stream.count(':')
        if colon_count >= 3:
            # Split the string by ":", then join back until the 3rd ":"
            parts = stream.split(':')
            required_part = ':'.join(parts[1:3])
            extracted_details.append(required_part)
    
    pattern = re.compile(r'(\d+)\((.*?)\): (.*)')
    
    # Initialize the result list
    result = []
    
    for item in extracted_details:
        # Find matches using the regex pattern
        match = pattern.match(item)
        if match:
            # Append the extracted values to the result list
            result.append([match.group(1), match.group(2), match.group(3)])
        else:
            # Handle cases where the parentheses are missing
            match = re.match(r'(\d+): (.*)', item)
            if match:
                result.append([match.group(1), '', match.group(2)])
    
    return result



def upload_video(request):
    if request.method == 'POST':
        file = request.FILES['file']
        video = Video.objects.create(file=file, title=file.name)
        process_video(video)
        return redirect('video_list')
    return render(request, 'upload.html')


def parse_subtitles(raw_data):
    subtitles = raw_data.strip().split('\n\n')
    subtitles.pop(0)
    parsed_subtitles = []
    for block in subtitles:
        lines = block.split('\n')
        time_range = lines[0]
        text = ' '.join(lines[1:])
        start, end = time_range.split(' --> ')
        parsed_subtitles.append({
            'start': start,
            'end': end,
            'text': text
        })
    return json.dumps(parsed_subtitles)


def search_video(request,id):
    results = Video.objects.get(id=id)
    raw_subtitles = results.subtitles.get(language = 'eng').content
    parsed_subtitles = parse_subtitles(raw_subtitles)
    print(parsed_subtitles)
    return render(request, 'search_results.html', {'results': results, 'parsed_subtitles':parsed_subtitles})

def search_subtitle(request):
    pass


def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

