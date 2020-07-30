#coding=utf-8
from BaseHTTPServer import BaseHTTPRequestHandler
import cgi

class   PostHandler(BaseHTTPRequestHandler):
    # 接收客户端发送的post请求
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     }
        )
        # 发送网络码
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %sn ' % str(self.client_address) )
        self.wfile.write('User-agent: %sn' % str(self.headers['user-agent']))
        self.wfile.write('Path: %sn'%self.path)
        self.wfile.write('Form data:n')
        num = 1
        for field in form.keys():
            field_item = form[field]
            filename = field_item.filename
            filevalue  = field_item.value
            filesize = len(filevalue)#文件大小(字节) 
            savefile = '/root/ocr_pytorch_master/test_images/'+ str(num) +'.png'
            while os.path.exists(savefile):
                num = num + 1
                savefile = '/root/ocr_pytorch_master/test_images/'+ str(num) +'.png'
                if (not os.path.exists(savefile)):
                    break
            savefile = '/root/ocr_pytorch_master/test_images/'+ str(num) +'.png'
            with open(savefile,'wb') as f:
                f.write(filevalue)
        return

def StartServer():
    from BaseHTTPServer import HTTPServer
    sever = HTTPServer(("",8080),PostHandler)
    sever.serve_forever()

if __name__=='__main__':
    num = 0
    StartServer()