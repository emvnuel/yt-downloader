import os
import tempfile
import shutil
from flask import Flask, request, jsonify, send_file, after_this_request, render_template
from pytubefix import YouTube
import ffmpeg

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_video():
    url = request.args.get('url')
    resolution = request.args.get('resolution')
    
    if not url or not resolution:
        return jsonify({'error': 'Missing URL or resolution parameter'}), 400

    temp_dir = tempfile.mkdtemp()
    
    @after_this_request
    def cleanup(response):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            app.logger.error(f"Cleanup error: {e}")
        return response

    try:
        yt = YouTube(url, 'WEB')
        output_path = os.path.join(temp_dir, 'out.mp4')
        output_audio_path = os.path.join(temp_dir, 'out.mp3')

        audio_stream = yt.streams.filter(
            only_audio=True,
            file_extension="mp4",
            type="audio"
        ).order_by('abr').desc().first()

        video_path = os.path.join(temp_dir, 'video.mp4')
        audio_path = os.path.join(temp_dir, 'audio.m4a')
        
        audio_stream.download(output_path=temp_dir, filename='audio.m4a')

        if (resolution == 'audio'):
            ffmpeg.input(audio_path).output(output_audio_path, acodec='libmp3lame').run()
            return send_file(
                output_audio_path,
                as_attachment=True,
                download_name=f"{yt.title}.mp3",
                mimetype='audio/mp3'
            )
        
        video_stream = yt.streams.filter(
            progressive=False,
            file_extension="mp4",
            res=resolution,
            type="video"
        ).first()

        video_stream.download(output_path=temp_dir, filename='video.mp4')

        try:
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)
            ffmpeg.output(
                audio_input,
                video_input,
                output_path,
                preset='superfast', 
            ).run()
        except ffmpeg.Error as e:
            app.logger.error(f"FFmpeg error: {e.stderr.decode()}")
            return jsonify({'error': 'Video processing failed'}), 500

        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{yt.title}.mp4",
            mimetype='video/mp4'
        )

    except Exception as e:
        app.logger.error(f"Processing error: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/video-info')
def video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    try:
        yt = YouTube(url, 'WEB')
        
        video_streams = yt.streams.filter(
            progressive=False, 
            file_extension="mp4",
            type="video"
        )
        
        resolutions = sorted(
            {stream.resolution for stream in video_streams if stream.resolution},
            key=lambda x: int(x.replace('p', '')),
            reverse=True
        )

        resolutions.append('audio')

        return jsonify({
            'title': yt.title,
            'thumbnail_url': yt.thumbnail_url,
            'resolutions': resolutions
        })

    except Exception as e:
        app.logger.error(f"Error getting video info: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)