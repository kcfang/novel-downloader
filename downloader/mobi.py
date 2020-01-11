import os
import subprocess
import shutil
import json
import tempfile

from generator import Generator
from crawler import settings


class MobiGenerator(Generator):
    filetype = "mobi"

    def __init__(self, info):
        super().__init__(info)
        self.work_dir = tempfile.mkdtemp(dir=os.getcwd())

    # def __del__(self):
    #     if os.path.isdir(self.work_dir):
    #         shutil.rmtree(self.work_dir)

    def template(self, f):
        return os.path.join('template', f)

    def rotate_quote(self, line):
        line = line.replace(u'「', u'﹁')
        line = line.replace(u'」', u'﹂')
        line = line.replace(u'（', u'︵')
        line = line.replace(u'）', u'︶')
        line = line.replace(u'《', u'︽')
        line = line.replace(u'》', u'︾')
        line = line.replace(u'『', u'﹃')
        line = line.replace(u'』', u'﹄')
        return line

    def gen_ncx(self, tocs):
        text = []
        index = 1
        for i, chapter in tocs:
            text.append('<navPoint id="navpoint-{}" playOrder="{}">\
                        <navLabel><text>{}</text></navLabel>\
                        <content src="chapter{}.html"/></navPoint>'.format(i, i, chapter, i))

        with open(self.template("temp.ncx"), "r") as temp:
            template = temp.read()

        with open(os.path.join(self.work_dir, "novel.ncx"), "w") as ncx:
            ncx.write(template.replace("@TEXT@", "\n".join(text)))

    def gen_toc(self, tocs):
        text = []
        index = 1
        for i, chapter in tocs:
            text.append('<li><a href="chapter{}.html">{}</a></li>'.format(i, chapter))

        with open(self.template("temp.toc"), "r") as temp:
            template = temp.read()

        with open(os.path.join(self.work_dir, "toc.html"), "w") as ncx:
            ncx.write(template.replace("@TEXT@", "\n".join(text)))


    def gen_opf(self, tocs, title):
        manifest = []
        spine = []
        for i, chapter in tocs:
            chapter = 'chapter{}'.format(i)
            manifest.append('<item id="{}" media-type="text/x-oeb1-document" href="{}.html"></item>'.format(chapter, chapter))
            spine.append('<itemref idref="{}"/>'.format(chapter))

        with open(self.template("temp.opf"), "r") as temp:
            t = temp.read()

        images = self.info.get('images')
        if images:
            cover = os.path.join(settings.IMAGES_STORE, self.info.get('images')[0]['path'])
        else:
            cover = self.template('cover.jpg')

        shutil.copy(cover, self.work_dir)
        cover = os.path.join(self.work_dir, os.path.basename(cover))

        with open(os.path.join(self.work_dir, "novel.opf"), "w") as ncx:
            t = t.replace("@MANIFEST@", "\n".join(manifest))
            t = t.replace("@SPINE@", "\n".join(spine))
            t = t.replace("@TITLE@", title)
            t = t.replace("@COVER@", cover)
            ncx.write(t)

    def generate_chapter(self, text, index):
        template = None
        with open(self.template("chapter_temp.html"), "r") as temp:
            template = temp.read()

        with open(os.path.join(self.work_dir, "chapter{}.html".format(str(index))), "w") as chapter:
            chapter.write(template.replace("@TEXT@", "\n".join(text)))

    def gen_file(self, targets):
        content = []
        tocs = []
        shutil.copy(self.template("temp.css"), self.work_dir)
        book = self.get_file_path(targets)
        title = self.info['title']

        for f in targets:
            with open(self.join_path(f), 'r') as fd:
                j = json.load(fd)
            index = f.split(".")[0]
            tocs.append((index, j['chapter']))
            content = [
                '<h1 id="{}">{}</h1>'.format(index, self.rotate_quote(j['chapter'])),
            ]
            for line in j['text']:
                content.append('<p>{}</p>'.format(self.rotate_quote(line)))

            self.generate_chapter(content, index)

        self.gen_ncx(tocs)
        self.gen_toc(tocs)
        self.gen_opf(tocs, title)
        try:
            cmd = [
                os.path.join(os.getcwd(), 'kindlegen'),
                os.path.join(self.work_dir, 'novel.opf'),
                '-o', os.path.basename(book)
            ]
            print(" ".join(cmd))
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "error" in e.output.decode():
                raise e

        print("Generate - {}.".format(book))
        os.makedirs(os.path.dirname(book), exist_ok=True)
        os.rename(os.path.join(self.work_dir, os.path.basename(book)), book)

        self.renew_workdir()
        return book

    def renew_workdir(self):
        if os.path.isdir(self.work_dir):
            shutil.rmtree(self.work_dir)
        self.work_dir = tempfile.mkdtemp(dir=os.getcwd())
