#!/usr/bin/env python3

import re
import sys
import argparse
import os
import glob
import shutil
import cv2
import ffmpeg
import datetime
import youtube_dl
import subprocess

def load_parameters(file_name="init.txt"):
    parameters = {}
    with open(file_name, encoding='utf-8') as f:
        origin = f.readlines()
        lines = []
        for line in origin:
            lines.append(line[:line.find("#")].replace("\n", ""))
        for line in lines:
            elements = line.split()
            if len(elements) == 2:
                print(elements)
                parameters[elements[0]] = elements[1]
    return parameters

def download_youtube_file(file_name="youtube_url.txt"):
    url_list = []
    line_list = []
    with open(file_name, encoding='utf-8') as f:
        for line in f.readlines():
            url = line[:line.find("#")].strip()
            line_list.append(url)
            if ("https://www.youtube.com/watch?v=" in url) or ("https://youtu.be/" in url):
                url_list.append(url)
    if len(url_list) > 0:
        print("Youtube URL Found!!")
        for i, url in enumerate(url_list):
            print("{:02d}: ".format(i), url)
    ydl_opt = {'outtmpl': 'TargetFiles/%(id)s%(ext)s'}
    if len(url_list) > 0:
        with youtube_dl.YoutubeDL(ydl_opt) as ydl:
            ydl.download(url_list)


def set_arguments(parser):
    parser.add_argument('-i', '--input_folder_name', default='TargetFiles')
    parser.add_argument('-s', '--init', default='init.txt')

    return parser.parse_args()

def make_py_file(video_file_name, A, B, python_file_name="avidemux_cli_run.py"):
    with open(python_file_name, "w", encoding='utf-8') as f:
        f.write("#PY  <- Needed to identify #\n")
        f.write("#--automatically built--\n")
        f.write("\n")
        f.write("adm = Avidemux()\n")
        f.write("adm.loadVideo(\"" + str(os.path.abspath(video_file_name)) + "\")\n")
        f.write("adm.clearSegments()\n")
        f.write("adm.videoCodec(\"Copy\")\n")
        f.write("adm.audioClearTracks()\n")
        f.write("adm.setSourceTrackLanguage(0,\"unknown\")\n")
        f.write("adm.audioAddTrack(0)\n")
        f.write("adm.audioCodec(0, \"copy\")\n")
        f.write("adm.audioSetDrc(0, 0)\n")
        f.write("adm.audioSetShift(0, 0,0)\n")
        f.write("adm.setContainer(\"MP4\", \"muxerType=0\", \"useAlternateMp3Tag=True\")\n")
        f.write("adm.addSegment(0, 0, 10000000000000000)\n")
        f.write("adm.markerA = " + str(A * 1000000) +"\n")
        f.write("adm.markerB = " + str(B * 1000000) +"\n")

def get_cmd_lines(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break

def check_vfr(file_name):
    cmd = "ffmpeg -ss 0 -i " + file_name + " -t 60 -an -vf vfrdet -f null -"
    lines = []
    for line in get_cmd_lines(cmd):
        # print(line.strip().decode('utf-8'))
        lines.append(line)

    results = lines[-1].strip().decode('utf-8').split()
    value = 0
    for result in results:
        if "VFR" in result:
            value = float(result.split(":")[-1])
    if value == 0:
        return 0
    else:
        return -1

    # (
    #     ffmpeg
    #     .input(file_name, ss=0, t=60)
    #     .output("-", vf="vfrdet", f="NULL")
    #     .run()
    # )
    # process = (
    #     ffmpeg
    #     .input(file_name)
    #     .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    #     .run_async(pipe_stdout=True, pipe_stderr=True)
    # )
    # out, err = process.communicate()

    

def main():

    parser = argparse.ArgumentParser(description="Kill Digest Maker for Splatoon videos")
    args = set_arguments(parser)

    print(args.input_folder_name)
    param = load_parameters(args.init)

    download_youtube_file()

    if int(param["SKIP_CUT_OUT"]) == 0:
        target_files=sorted(glob.glob("./" + args.input_folder_name + "/**.*", recursive=True))

        if os.path.isdir('./temp'):
            shutil.rmtree('./temp')
        os.mkdir('./temp')
        
        if not os.path.isdir('./KillDigestVideos'):
            os.mkdir('./KillDigestVideos')

        for f in target_files:
            if check_vfr(f) < 0:
                print("VFR file is detected!!!")
                target_files.remove(f)
                cfr_file_name = "./" + args.input_folder_name + "/" +  os.path.splitext(os.path.basename(f))[0] + "_cfr.mp4"
                if cfr_file_name not in target_files:
                    (
                        ffmpeg
                        .input(f)
                        .output(cfr_file_name, vsync="cfr", vcodec=param["VIDEO_CODEC"])
                        .run()
                    )
                    target_files.append(cfr_file_name)
        print(target_files)

        max_height_size = 0
        for f in target_files:
            cap = cv2.VideoCapture(f)
            if not cap.isOpened():
                continue
            if max_height_size < cap.get(cv2.CAP_PROP_FRAME_HEIGHT):
                max_height_size = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            cap.release()

            video_info = ffmpeg.probe(f)
            print(video_info)
        if int(param["MOVIE_SIZE_DESIGNATION"]) == 1:
            max_height_size = int(param["MOVIE_SIZE_HEIGHT"])

        out_file_count=0

        for video_id, video_file_name in enumerate(target_files):
            cap = cv2.VideoCapture(video_file_name)
            if not cap.isOpened():
                continue
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            template = cv2.imread("templates/template.jpg")
            if int(param["WIN_DETECTION"]) == 1:
                win_template = cv2.imread("templates/win_template.jpg")
            if int(param["LOSE_DETECTION"]) == 1:
                lose_template = cv2.imread("templates/lose_template.jpg")

            temp_scale = float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) / 1080.0

            template = cv2.resize(template, (int(template.shape[1] * temp_scale), int(template.shape[0] * temp_scale)))
            if int(param["WIN_DETECTION"]) == 1:
                win_template = cv2.resize(win_template, (int(win_template.shape[1] * temp_scale), int(win_template.shape[0] * temp_scale)))
            if int(param["LOSE_DETECTION"]) == 1:
                lose_template = cv2.resize(lose_template, (int(lose_template.shape[1] * temp_scale), int(lose_template.shape[0] * temp_scale)))

            # cv2.imwrite("template_resize.jpg", template)
            # cv2.imwrite("win_templatee_resize.jpg", win_template)
            # cv2.imwrite("lose_template_resize.jpg", lose_template)

            key_frames = []
            if int(param["WIN_DETECTION"]) == 1 or int(param["LOSE_DETECTION"]) == 1 or int(param["SHOW_RESULT"]) == 1:
                key_result_frames = []
            i = 0
            while(cap):
                i+=1
                if i % int(fps * float(param["SEARCHING_FRAME_INTERVAL"])) != 0:
                    cap.grab()
                    continue
                ret, frame = cap.read()
                if not ret:
                    break

                # timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                # print("## timestamp {:04.4f}[s] frame/fps {:04.4f}[s] ".format(timestamp/1000.0, i/fps), end="")

                print("[Video {}/{}] Searching kill frame... {:3.2f} [%] done.".format(video_id+1, \
                    len(target_files), i * 100 / frame_num), end='')

                # searching kill frame
                frame_rect = frame[int(992.0 * temp_scale): int((992.0 + 44.0) * temp_scale), \
                    int(920.0 * temp_scale): int((920.0 + 260.0)  * temp_scale)]
                result = cv2.matchTemplate(frame_rect, template, cv2.TM_CCORR_NORMED)
                _, max_val, _, _ =  cv2.minMaxLoc(result)
                if (max_val > float(param["TAMPLATE_MATCHING_THRESHOLD"])):
                    print(" Kill scene detected!!!", end='')
                    key_frames.append(i)
                    # cv2.imwrite("debug.jpg", frame_rect)

                if int(param["WIN_DETECTION"]) == 1 or int(param["SHOW_RESULT"]) == 1:
                    frame_win = frame[int(54.0 * temp_scale): int((54.0 + 74.0) * temp_scale), \
                        int(36.0 * temp_scale): int((36.0 + 206.0) * temp_scale)]
                    result_win = cv2.matchTemplate(frame_win, win_template, cv2.TM_CCORR_NORMED)
                    _, max_val, _, _ =  cv2.minMaxLoc(result_win)
                    if (max_val > float(param["TAMPLATE_MATCHING_THRESHOLD"])):
                        print(" Win scene detected!!!", end='')
                        key_result_frames.append(i)

                if int(param["LOSE_DETECTION"]) == 1 or int(param["SHOW_RESULT"]) == 1:
                    frame_lose = frame[int(64.0 * temp_scale): int((64.0 + 68.0) * temp_scale), \
                        int(32.0 * temp_scale): int((32.0 + 268.0) * temp_scale)]
                    result_lose = cv2.matchTemplate(frame_lose, lose_template, cv2.TM_CCORR_NORMED)
                    _, max_val, _, _ =  cv2.minMaxLoc(result_lose)
                    if (max_val > float(param["TAMPLATE_MATCHING_THRESHOLD"])):
                        print(" Lose scene detected!!!", end='')
                        key_result_frames.append(i)

                print("")
            
            key_frame_group = []
            if len(key_frames) > 1:
                prev_value = key_frames[0]
                local_key_frames = []
                local_key_frames.append(prev_value)
                for value in key_frames[1:]:
                    if value - prev_value > fps * float(param["CONNECTING_INTERVAL"]) * float(param["SEARCHING_FRAME_INTERVAL"]):
                        key_frame_group.append(local_key_frames)
                        local_key_frames = []
                    local_key_frames.append(value)
                    prev_value = value
                if len(local_key_frames) > 0:
                    key_frame_group.append(local_key_frames)
                for local in key_frame_group:
                    print("key frame: ",local)

            if int(param["WIN_DETECTION"]) == 1 or int(param["LOSE_DETECTION"]) == 1 or int(param["SHOW_RESULT"]) == 1:
                key_result_frame_group = []
                if len(key_result_frames) > 1:
                    prev_value = key_result_frames[0]
                    local_key_frames = []
                    local_key_frames.append(prev_value)
                    for value in key_result_frames[1:]:
                        if value - prev_value > fps * 2.0 * float(param["SEARCHING_FRAME_INTERVAL"]):
                            key_result_frame_group.append(local_key_frames)
                            local_key_frames = []
                        local_key_frames.append(value)
                        prev_value = value
                    if len(local_key_frames) > 0:
                        key_result_frame_group.append(local_key_frames)

                for index in range(len(key_result_frame_group)):
                    key_result_frame_group[index].insert(0, int(key_result_frame_group[index][0] \
                        + float(param["ADDITIONAL_TIME_BEFORE_KILL"]) * fps - 2.5))
                    key_result_frame_group[index].append(int(key_result_frame_group[index][-1] \
                        - float(param["ADDITIONAL_TIME_AFTER_KILL"]) * fps - 0.5))
                        
                if int(param["SHOW_RESULT"]) == 1:
                    new_key_result_frame_group = []
                    for group in key_result_frame_group:
                        if int(param["WIN_DETECTION"]) == 1 or int(param["LOSE_DETECTION"]) == 1:
                            if len(group[1:-2]) > 1:
                                new_key_result_frame_group.append(group[1:-2])
                        if len(group[:-1]) > 1:
                            new_key_result_frame_group.append([int(x + 9 * fps) for x in group[:-1]])
                    key_result_frame_group = new_key_result_frame_group

                for local in key_result_frame_group:
                    print("key result frame: ",local)

                if int(param["WIN_DETECTION"]) == 1 or int(param["LOSE_DETECTION"]) == 1 or int(param["SHOW_RESULT"]) == 1:
                    key_frame_group.extend(key_result_frame_group)
                    key_frame_group = sorted(key_frame_group, key=lambda x: x[0])

                for local in key_frame_group:
                    print("key frame: ",local)

            cap.release()

            # movie cut out
            for local_key_frames in key_frame_group:
                if len(local_key_frames) < float(param["CANDIDATE_FRAME_NUM"]):
                    continue
                # if int(param["CUT_OUT_ENCORD"]) == 1:

                ## Following codes for vrf format but do not work well...
                # start_frame = int(local_key_frames[0] - float(param["ADDITIONAL_TIME_BEFORE_KILL"])*fps)
                # end_frame = int(local_key_frames[-1] + float(param["ADDITIONAL_TIME_AFTER_KILL"])*fps)
                # stream = ffmpeg.input(video_file_name)
                # stream = ffmpeg.trim(stream, start_frame=start_frame, end_frame=end_frame)
                # stream = ffmpeg.output(stream, "temp/" + "{:04d}-".format(out_file_count) + os.path.splitext(os.path.basename(video_file_name))[0].replace(" ", "_") + ".mp4", \
                #     t=((local_key_frames[-1]-local_key_frames[0])/float(fps) + float(param["ADDITIONAL_TIME_AFTER_KILL"])), \
                #     filter_complex=("[0:v]scale=-1:" + str(max_height_size) + "[tmp];[tmp]setpts=PTS-STARTPTS[out]"), map="[out]", vcodec=param["VIDEO_CODEC"])
                # ffmpeg.run(stream)

                stream = ffmpeg.input(video_file_name, ss=(local_key_frames[0]/fps - float(param["ADDITIONAL_TIME_BEFORE_KILL"])),\
                    t=((local_key_frames[-1]-local_key_frames[0])/fps + float(param["ADDITIONAL_TIME_AFTER_KILL"])))
                stream = ffmpeg.output(stream, "temp/" + "{:04d}-".format(out_file_count) + os.path.splitext(os.path.basename(video_file_name))[0].replace(" ", "_") + ".mp4", \
                    vf="scale=-1:" + str(max_height_size), vcodec=param["VIDEO_CODEC"])
                ffmpeg.run(stream)

                # else:
                #     make_py_file(video_file_name, local_key_frames[0]/fps - float(param["ADDITIONAL_TIME_BEFORE_KILL"]),\
                #         local_key_frames[-1]/fps + float(param["ADDITIONAL_TIME_AFTER_KILL"]))
                #     cmd = ["avidemux3_cli", "--run", "\"" + os.path.abspath("avidemux_cli_run.py") + "\"", "--save", \
                #         "temp/" + "{:04d}-".format(out_file_count) + os.path.splitext(os.path.basename(video_file_name))[0].replace(" ", "_") + ".mp4",\
                #             "--quit"]
                #     subprocess.call(cmd, shell=True)

                
                out_file_count+=1
                

    if int(param["SKIP_CONCATENATION"]) == 0:
        file_list = sorted(glob.glob("temp/*.mp4"))
        with open("./temp/file_list.txt", "w") as f:
            f.write("\n".join([f"file '{os.path.basename(line)}'" for line in file_list]))
        
        if len(file_list) > 0:
            stream = ffmpeg.input("./temp/file_list.txt", f="concat", safe=0)
            if int(param["CONCATENATION_ENCORD"]) == 1:
                stream = ffmpeg.output(stream, './KillDigestVideos/'+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".mp4", vcodec=param["VIDEO_CODEC"])
            else:
                stream = ffmpeg.output(stream, './KillDigestVideos/'+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".mp4", c="copy")
            ffmpeg.run(stream)






            
            





    




if __name__ == '__main__':
    main()