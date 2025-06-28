import os
import uuid
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import FileResponse
from yt_dlp import YoutubeDL

def youtube_downloader_view(request):
    context = {}

    if request.method == 'POST':
        url = request.POST.get('video_url')
        format_selected = request.POST.get('video_format', '360p')
        context['video_url'] = url
        context['video_format'] = format_selected

        video_id = str(uuid.uuid4())
        base_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(base_path, exist_ok=True)

        format_map = {
            '360p': '18',
            '720p': '22',
            '1080p': '137+140',
            'audio': 'bestaudio',
        }

        selected_format = format_map.get(format_selected, '18')
        output_path = os.path.join(base_path, f'{video_id}.%(ext)s')

        ydl_opts = {
            'format': selected_format,
            'outtmpl': output_path,
            'noplaylist': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                context['video_title'] = info.get('title', 'Unknown Title')
                filesize = info.get('filesize') or info.get('filesize_approx')
                context['video_size'] = f"{round(filesize / (1024 * 1024), 2)} MB" if filesize else "N/A"
        except Exception as e:
            context['error'] = f"⚠️ Download info error: {str(e)}"

    elif request.method == 'GET' and 'download' in request.GET:
        url = request.GET.get('download')
        format_selected = request.GET.get('format', '360p')
        video_id = str(uuid.uuid4())
        base_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(base_path, exist_ok=True)

        selected_format = {
            '360p': '18',
            '720p': '22',
            '1080p': '137+140',
            'audio': 'bestaudio',
        }.get(format_selected, '18')

        output_path = os.path.join(base_path, f'{video_id}.%(ext)s')

        ydl_opts = {
            'format': selected_format,
            'outtmpl': output_path,
            'noplaylist': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            return FileResponse(open(filename, 'rb'), as_attachment=True, filename=os.path.basename(filename))
        except Exception as e:
            context['error'] = f"❌ Download failed: {str(e)}"

    return render(request, 'ytdownloader/youtube_downloader.html', context)

'''

def youtube_downloader_view(request):
    context = {}
    if request.method == 'POST':
        url = request.POST.get('video_url')
        format_selected = request.POST.get('video_format', '360p')
        video_id = str(uuid.uuid4())
        base_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(base_path, exist_ok=True)

        try:
            format_map = {
                '360p': '18',
                '720p': '22',
                'audio': 'bestaudio',
            }
            selected_format = format_map.get(format_selected, '18')
            output_path = os.path.join(base_path, f'{video_id}.%(ext)s')

            ydl_opts = {
                'format': selected_format,
                'outtmpl': output_path,
                'noplaylist': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # ✅ Now serve the file as a download
            return FileResponse(open(filename, 'rb'), as_attachment=True, filename=os.path.basename(filename))

        except Exception as e:
            context['error'] = f"❌ Error: {str(e)}"

    return render(request, 'ytdownloader/youtube_downloader.html', context)
'''
