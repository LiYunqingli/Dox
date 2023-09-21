using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Threading;
using System.Windows.Forms;
using System.Net.Http;
using System.Globalization;

//2023/05/20
//作者：云清璃

//2023/08/22
//作者：云清璃



namespace Dox_1._0_
{
    public class EncryptionHelper//加密所有文件的类
    {
        public static char[] TextEncrypt(string content, string secretKey)
        {
            char[] data = content.ToCharArray();
            char[] key = secretKey.ToCharArray();
            for (int i = 0; i < data.Length; i++)
            {
                data[i] ^= key[i % key.Length];
            }
            return data;
        }

        public static string TextDecrypt(char[] data, string secretKey)
        {
            char[] key = secretKey.ToCharArray();
            for (int i = 0; i < data.Length; i++)
            {
                data[i] ^= key[i % key.Length];
            }
            return new string(data);
        }

        public static void Lock(string a)//path style key
        {
            string[] sp = a.Split(' ');
            string path = "";
            string key = "";
            string style = "";
            string savePath = "";
            if (sp.Length < 3)
            {
                Program.console("red", "参数不全", "Incomplete parameters");
                Program.console("red", "lock(string path, string style, string key)", "lock(string path, string style, string key");
                return;
            }
            else
            {
                path = sp[0];
                //path = Program.quanju + "\\" + sp[0];
                style = sp[1];
                key = sp[2];
            }
            string txt = "";
            string content = txt;
            string secretKey = key;
            string encryptedText = "";
            string saveText = "";
            if (style == "DoxDel")//处理Dox内部解密(其他的代码处理用户的操作)
            {
                content = File.ReadAllText(path);
                char[] content_char = content.ToCharArray();
                // 调用解密函数
                if (!File.Exists(key))
                {
                    Program.console("red","您的Dox未应用密钥，请联系作者获取秘钥","");
                    //Console.Beep(432,50);
                    //Console.Beep(528,50);
                    //Console.Beep(440,50);
                    return;
                }
                secretKey = File.ReadAllText(key);
                char[] decryptedData = TextDecrypt(content_char, secretKey).ToArray();

                // 将解密后的数据转换为字符串
                string decryptedText = new string(decryptedData);

                Console.WriteLine(decryptedText);
                return;
            }
            try
            {
                txt = File.ReadAllText(path);
                savePath = "file.key.ok/" + path;
            }
            catch (Exception)
            {
                try
                {
                    path = Program.quanju + "\\" + sp[0];
                    txt = File.ReadAllText(path);
                    savePath = Program.quanju + "/file.key.ok/" + sp[0];
                }
                catch (Exception)
                {
                    Program.console("red", "lock: 无法找到文件" + path, "lock: cannot find file" + path);
                    Program.console("red", "请尝试使用cd命令进入该文件的目录或输入该文件的绝对路径再次尝试", "Please try using the cd command to enter the directory of the file or enter the absolute path of the file and try again");
                    return;
                }
            }
            if (style == "add")
            {
                // 调用加密函数
                char[] encryptedData = TextEncrypt(content, secretKey);

                // 将加密后的数据转换为字符串
                encryptedText = new string(encryptedData);

                //Console.WriteLine("加密后的文本: " + encryptedText);
                saveText = encryptedText;
            }
            else if (style == "del")
            {
                char[] content_char = content.ToCharArray();
                // 调用解密函数
                char[] decryptedData = TextDecrypt(content_char, secretKey).ToArray();

                // 将解密后的数据转换为字符串
                string decryptedText = new string(decryptedData);

                //Console.WriteLine("解密后的文本: " + decryptedText);
                saveText = decryptedText;

            }
            string directoryPath = Path.GetDirectoryName(savePath);        ///
            if (!Directory.Exists(directoryPath))
            {
                Directory.CreateDirectory(directoryPath);
            }                                          ///防止某一文件夹不存在，自动补全这股路径下的所有文件夹
            File.AppendAllText(savePath, saveText);

        }
    }
    class Program
    {
        public static string localpath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);//获取桌面的路径
        public static string quanju = "Dox:";//定义输出的路径
        public static string lang = localhost("language", "");//全局语言

        public static string localhost(string one, string two)// 识别本地文件
        {
            string str = System.Environment.CurrentDirectory;
            if (one == "language")
            { 
                string rtn = "";
                try
                {
                    str = str + "\\set\\language";
                    StreamReader reader = new StreamReader(str, System.Text.Encoding.Default);
                    string line = reader.ReadLine();
                    if (line == "CN" || line == "cn")
                    {
                        rtn = "cn";
                    }
                    else if (line == "EN" || line == "en")
                    {
                        rtn = "en";
                    }
                    reader.Close();
                }
                catch (Exception)
                {
                    MessageBox.Show("Dox初始化文件失效,文件缺失\n\nNot file 'language'!", "文件缺失");
                    Environment.Exit(0);
                }
                return rtn;
            }
            else if (one == "local")
            {
                str = str + "\\model";
                try
                {
                    DirectoryInfo di = new DirectoryInfo(str);
                    Directory.CreateDirectory(str);
                    string[] folders = Directory.GetDirectories(str);//获取base文件夹下所有的文件夹路径
                    for (int i = 0; i < folders.Length; i++)
                    {
                        folders[i] = Path.GetFileName(folders[i]);//在路径中提取文件夹名
                    }
                    string a = "";
                    foreach (string shuchu in folders)
                    {
                        a += "\n" + shuchu;
                    }
                    if (a == "")
                    {
                        a = console("return","您未安装过任何模块，如需安装，请键入help install 获取帮助", "You have not installed any modules before. To install them, please type help install for assistance");
                    }
                    return a;
                }
                catch (Exception)
                {
                    Console.WriteLine("Warring!!!");
                }
                return "命令出现未知错误";
            }
            else
            {
                return "";
            }
        }
        public static string console(string style, string cn, string en)//输出内容，其中style是类型，包括（return语言 ,异常红，链接蓝，路径蓝，成功绿，警告黄）
        {
            if (style == "green")
            {
                Console.ForegroundColor = ConsoleColor.Green;

            }
            else if (style == "red")
            {
                Console.ForegroundColor = ConsoleColor.Red;
            }
            else if (style == "blue")
            {
                Console.ForegroundColor = ConsoleColor.Blue;
            }
            else if (style == "yellow")
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
            }
            else if (style == "return")
            {
                if (lang == "cn")
                {
                    return cn;
                }
                else
                {
                    return en;
                }
            }
            else
            {

            }
            if (lang == "cn")
            {
                Console.WriteLine(cn);
            }
            else
            {
                Console.WriteLine(en);
            }
            Console.ForegroundColor = ConsoleColor.White;
            return "";
        }
        static void check()//Dox自检函数（网络，本地文件是否缺失，能否连接Dox服务器，下载的文件是否损坏，路径是否存在等等，后续）
        {
            List<string> errors = new List<string>();
            console("", "\n文件检查\n", "\nfile check\n");
            console("blue", "检查Dox的组件以及文件是否完整", "Check if the System.Text.Encoding.UTF8 and files of Dox are complete");
            string[] dox_files_list = File.ReadAllLines("check/dox_files_list");//读取列表的每行放入每个元素里
            int _null = 0;
            for (int i = 0; i < dox_files_list.Length; i++)
            {
                if (dox_files_list[i] == "")
                {
                    _null = 1;
                    continue;
                }
                if (_null != 1)
                {
                    if (File.Exists(dox_files_list[i]))
                    {
                        console("green", "文件“" + dox_files_list[i] + "“存在", "File \"" + dox_files_list[i] + "\" does exist");
                    }
                    else
                    {
                        console("red", "文件“" + dox_files_list[i] + "“不存在", "File \"" + dox_files_list[i] + "\" does not exist");
                        errors.Add(console("return", "文件“" + dox_files_list[i] + "“存在", "File \"" + dox_files_list[i] + "\" does exist"));
                    }
                }
                else
                {
                    if (Directory.Exists(dox_files_list[i]))
                    {
                        console("green", "文件夹“" + dox_files_list[i] + "“存在", "Folder \"" + dox_files_list[i] + "\" does exist");
                    }
                    else
                    {
                        console("red", "文件夹“" + dox_files_list[i] + "“不存在", "Folder \"" + dox_files_list[i] + "\" does not exist");
                        errors.Add(console("return", "文件夹“" + dox_files_list[i] + "“不存在", "Folder \"" + dox_files_list[i] + "\" does not exist"));
                    }
                }
                Thread.Sleep(20);
            }
            console("", "\n网络测试\n", "\nNetwork Test\n");
            console("blue", "测试与www.baidu.com的连通性（仅测试）", "Testing connectivity with www.baidu.com (testing only)");
            string host = "www.baidu.com"; // 测试的主机

            Ping pingSender = new Ping();
            try
            {
                PingReply reply = pingSender.Send(host);
                if (reply.Status == IPStatus.Success)
                {
                    for (int i = 0; i <= 100; i++)//进度条
                    {
                        UpdateProgress(i, "yellow");
                        Thread.Sleep(10); // 模拟操作的延迟
                        Console.ForegroundColor = ConsoleColor.White;
                    }
                    console("green", "\n网络通畅！", "\nSmooth network!");
                    console("blue", "\n尝试向服务器发送请求数据", "\nAttempting to send request data to the server");
                    using (WebClient client = new WebClient())
                    {
                        string save_list_path = "ping.txt";
                        StreamReader reader = new StreamReader("ping_url", System.Text.Encoding.UTF8);
                        string line_url = reader.ReadLine();
                        try
                        {
                            client.DownloadFile(line_url, save_list_path);
                        }
                        catch (Exception)
                        {
                            console("red", "\n无法连接服务器，可能是作者未启动服务器，或您未在服务器开放时间访问（开放时间：上午8:00-晚上7:00或8:00前），若需要下载组件，请联系作者获取帮助", "\nUnable to connect to the server. It is possible that the author did not start the server or that you did not access it during server open hours (open hours: 9:00 am -7:00 pm or before 8:00 pm). If you need to download components, please contact the author for assistance");
                            errors.Add(console("return", "\n无法连接服务器，可能是作者未启动服务器，或您未在服务器开放时间访问（开放时间：上午8:00-晚上7:00或8:00前），若需要下载组件，请联系作者获取帮助", "\nUnable to connect to the server. It is possible that the author did not start the server or that you did not access it during server open hours (open hours: 9:00 am -7:00 pm or before 8:00 pm). If you need to download components, please contact the author for assistance"));
                        }
                        if (File.Exists("ping.txt"))
                        {
                            for (int i = 0; i <= 100; i++)//进度条
                            {
                                UpdateProgress(i, "yellow");
                                Thread.Sleep(10); // 模拟操作的延迟
                                Console.ForegroundColor = ConsoleColor.White;
                            }
                            console("green", "\n已成功从服务器接收数据", "\nSuccessfully received data from the server");
                            console("blue", "\n正在检查数据是否完整或编码正常", "\nChecking if the data is complete or encoding is normal");
                            for (int i = 0; i <= 100; i++)//进度条
                            {
                                UpdateProgress(i, "yellow");
                                Thread.Sleep(10); // 模拟操作的延迟
                                Console.ForegroundColor = ConsoleColor.White;
                            }
                            StreamReader reader1 = new StreamReader("ping.txt", System.Text.Encoding.UTF8);
                            try
                            {
                                if (reader1.ReadLine() != "true")
                                {
                                    console("red", "\n从服务器接收的数据能够正常读取，但并不是预期的内容，可能是服务器的数据文件出现变动或文件传输出现问题", "\nThe data received from the server can be read normally, but it is not the expected content. It may be due to changes in the server's data file or file transfer issues");
                                    errors.Add(console("return", "\n从服务器接收的数据能够正常读取，但并不是预期的内容，可能是服务器的数据文件出现变动或文件传输出现问题", "\nThe data received from the server can be read normally, but it is not the expected content. It may be due to changes in the server's data file or file transfer issues"));
                                }
                                else
                                {
                                    console("green", "\n数据完整，读取正常，能够连接服务器", "\nThe data is complete, the reading is normal, and the server can be connected");
                                }
                                reader1.Close();
                                File.Delete("ping.txt");
                            }
                            catch (Exception)
                            {
                                console("red", "\n接收的数据无法正常读取，可能是文件编码错误，或服务器数据异常，请联系作者处理。", "\nThe received data cannot be read properly. It may be due to file encoding errors or server data anomalies. Please contact the author for assistance.");
                                errors.Add(console("return", "\n接收的数据无法正常读取，可能是文件编码错误，或服务器数据异常，请联系作者处理。", "\nThe received data cannot be read properly. It may be due to file encoding errors or server data anomalies. Please contact the author for assistance."));
                                reader1.Close();
                                File.Delete("ping.txt");
                            }
                        }
                        
                    }
                }
                else
                {
                    console("red", "\n网络不通畅!", "\nThe network is not smooth!");
                    console("red", "请检查网络是否连接，并确保能够正常连接互联网", "Please check if the network is connected and ensure that you can connect to the internet normally");
                    errors.Add(console("return", "请检查网络是否连接，并确保能够正常连接互联网", "Please check if the network is connected and ensure that you can connect to the internet normally"));
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
                console("red", "\n网络不通畅!", "\nThe network is not smooth!");
                console("red", "请检查网络是否连接，并确保能够正常连接互联网", "Please check if the network is connected and ensure that you can connect to the internet normally");
                errors.Add(console("return", "请检查网络是否连接，并确保能够正常连接互联网", "Please check if the network is connected and ensure that you can connect to the internet normally"));
            }
            if (errors.Count != 0)
            {
                console("red", "\n\n====================", "\n\n====================");
                console("red", "\n\n共检查出" + errors.Count + "项错误\n\n", "\n\nCo inspection found " + errors.Count + " errors\n\n");
                foreach (string s in errors)
                {
                    console("red", s, s);
                }
            }
            else
            {
                console("green", "\n\n====================", "\n\n====================");
                console("green", "\n\n未检查出错误，若有疑问请联系开发者获取帮助", "\n\nNo errors were detected. If you have any questions, please contact the developer for assistance");
            }
        }
        static void update()//更新组件
        {
            
            string url = "https://739e87s017.goho.co/VERSION";

            using (HttpClient client = new HttpClient())
            {
                try
                {
                    HttpResponseMessage response = client.GetAsync(url).Result;
                    string content = response.Content.ReadAsStringAsync().Result;
                    string local_version = File.ReadAllText("version");
                    if(content != local_version)
                    {
                        console("blue","Dox有新版本更新，请键入update dox下载Dox的安装包，谢谢", "There is a new version update for Dox. Please type update dox to download the installation package for Dox. Thank you");
                    }
                    else
                    {
                        console("green","您的dox以及模块组件已经是最新版了", "Your DOS and module components are already the latest version");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"An error occurred: {ex.Message}");
                }
            }
            
            
            
        }
        static void help(string str)//帮助文档
        {
            string[] sp = str.Split(' ');
            string path = "base\\" + lang + "\\help";
            if (sp[0] == "")
            {
                EncryptionHelper.Lock(path + "\\any DoxDel key\\公钥（本地文件）");
            }
            else
            {
                try
                {
                    EncryptionHelper.Lock(path + "\\" + sp[0] + " DoxDel key\\公钥（本地文件）");
                }
                catch (Exception)
                {
                    console("red", "未找到关于" + sp[0] + "的帮助", "No help found for " + sp[0]);
                }
            }
        }
        static void show(string a)//查看Dox的一些内容
        {
            if (a == "model")
            {
                Console.WriteLine(localhost("local", ""));
            }
            else
            {
                console("red", "\n无效的参数：" + a, "\nInvalid parameter: " + a);
            }
        }
        static void set(string str)//设置Dox的配置，例如语言
        {
            string[] splitted = str.Split(' ');
            if (splitted[0] == "language")
            {
                string path = System.Environment.CurrentDirectory;
                path = path + "\\set\\language";
                if (splitted.Length == 1)
                {
                    console("red", "\n你的语法存在错误：“language”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'language'?");
                }
                else
                {
                    if (splitted[1] != "cn" && splitted[1] != "en" && splitted[1] != "CN" && splitted[1] != "EN")
                    {
                        console("red", "\n无法找到该语言：" + splitted[1], "\nUnable to find the language: " + splitted[1]);
                        return;
                    }
                    if (localhost("language", "") == "cn")
                    {
                        if (splitted[1] == "cn" || splitted[1] == "CN")
                        {
                            Console.WriteLine("\nlanguage：你的当前语言已经是CN简体中文了。");
                            if (lang != "cn" && lang != "CN")
                            {
                                Console.WriteLine("但是检测到您当前的语言并未生效，请键入“exit(1)”命令重启程序应用设置");
                            }
                            return;
                        }
                    }
                    else
                    {
                        if (splitted[1] == "en" || splitted[1] == "EN")
                        {
                            Console.WriteLine("\nlanguage: Your current language is already EN Modren English.");
                            if (lang != "en" && lang != "EN")
                            {
                                Console.WriteLine("However, it has been detected that your current language is not valid. Please type the \"exit (1)\" command to restart the program and apply settings");
                            }
                            return;
                        }
                    }
                    File.WriteAllText(path, splitted[1]);//更改language文件的内容
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    if (lang == "cn")
                    {
                        Console.Write("立即重启程序生效（Y/N）\n请输入：");
                    }
                    else
                    {
                        Console.Write("Immediate restart of the program takes effect (Y/N)\nPlease Enter:");
                    }
                    string a = Console.ReadLine();
                    Console.ForegroundColor = ConsoleColor.White;
                    if (a == "y" || a == "Y")
                    {
                        System.Diagnostics.Process.Start(Application.ExecutablePath);
                        Environment.Exit(0);//重启
                    }
                }
            }
            else
            {
                console("red", "\n你的语法存在错误：无效的参数" + splitted[0], "\nThere is an error in your grammar: Invalid parameter " + splitted[0]);
            }
        }
        static void install(string canshu)//安装命令，提供安装Dox的模块，以及卸载更新
        {
            string[] sp = canshu.Split(' ');
            if (sp.Length == 1)
            {
                if (canshu == "-s")//查看模块列表
                {
                    if (!File.Exists("model/modellist.doxmodellist"))
                    {
                        console("red", "列表文件不存在，请键入install下载更新模块列表", "The list file does not exist. Please type install to download and update the module list");
                        return;
                    }
                    string[] lines = File.ReadAllLines("model/modellist.doxmodellist");
                    Console.WriteLine("");
                    for (int i = 0; i < lines.Length; i++)
                    {
                        console("blue", lines[i], lines[i]);
                        i++;
                    }
                    return;
                }
                if(canshu == "-l")
                {
                    console("blue","请输入模块包路径：", "Please enter the module package path:");
                    string modelpath = Console.ReadLine();
                    if (!File.Exists(modelpath))
                    {
                        console("red", "\n文件不存在，请检查文件路径，再试一次", "\nThe file does not exist. Please check the file path and try again");
                        return;
                    }
                    else
                    {
                        string fileUrl1 = modelpath;
                        console("blue", fileUrl1, fileUrl1);
                        string extractPath1 = @"model"; // 解压目标路径
                        console("","扫描文件，验证文件的安全性", "Scan files to verify their security");
                        for (int i = 0; i <= 100; i++)
                        {
                            UpdateProgress(i, "green");
                            Thread.Sleep(5); // 模拟操作的延迟
                            Console.ForegroundColor = ConsoleColor.White;
                        }
                        console("", "解压模块包", "Decompression module package");
                        ZipFile.ExtractToDirectory(fileUrl1, extractPath1);
                        for (int i = 0; i <= 100; i++)
                        {
                            UpdateProgress(i, "blue");
                            Thread.Sleep(10); // 模拟操作的延迟
                            Console.ForegroundColor = ConsoleColor.White;
                        }
                        // 解压文件

                        console("green", "文件解压成功！", "File decompression successful!");
                        console("blue", "正在执行Dox优化......", "Performing Dox optimization...");
                        Thread.Sleep(2000);
                    }
                    return;
                }
                string download = "";
                if (canshu == "")//更新列表
                {
                    try
                    {
                        console("", "\n更新模块列表\n", "\nUpdate module list\n");
                        Thread.Sleep(100);
                        Console.Write("model_list_url: ");
                        string save_list_path = "model\\modellist.doxmodellist";
                        StreamReader reader = new StreamReader("model_list_url", System.Text.Encoding.UTF8);
                        string line_url = reader.ReadLine();
                        console("blue", line_url, line_url);
                        Thread.Sleep(1000);
                        console("", "获取列表", "Get List");
                        using (WebClient client = new WebClient())
                        {
                            // 下载modellist列表文件
                            client.DownloadFile(line_url, save_list_path);
                            long fileSize = long.Parse(client.ResponseHeaders.Get("Content-Length"));
                            console("", "文件大小" + file_size(fileSize.ToString()), "file size " + file_size(fileSize.ToString()));
                            for (int i = 0; i <= 100; i++)//进度条
                            {
                                UpdateProgress(i, "green");
                                Thread.Sleep(10); // 模拟操作的延迟
                                Console.ForegroundColor = ConsoleColor.White;
                            }
                            console("green", "\n列表更新成功！", "List updated successfully!");
                        }
                        return;
                    }
                    catch (Exception)
                    {
                        console("red", "\n出现未知异常，可能是读取model列表大小失败或文件下载失败\n\n", "\nAn unknown exception occurred, possibly due to a failure to read the model list size or file download failure\n\n");
                        Thread.Sleep(1000);
                        console("red", "正在启动Dox自检...", "Starting Dox self test...");
                        Thread.Sleep(5000);
                        check();
                    }
                }
                else
                {
                    if (!File.Exists("model/modellist.doxmodellist"))
                    {
                        console("red", "列表文件不存在，请键入install下载更新模块列表", "The list file does not exist. Please type install to download and update the module list");
                        return;
                    }
                    /*if (canshu == "tcp-chat-root")
                    {
                        console("yellow", "该控件仅限于开发者使用，请输入密码", "This control is only for developers to use. Please enter a password");
                        string aaa = Console.ReadLine();
                        if (aaa != "adminapp")
                        {
                            return;
                        }
                    }*/
                    string[] lines = File.ReadAllLines("model/modellist.doxmodellist");
                    for (int i = 0; i < lines.Length; i++)
                    {
                        if (canshu == lines[i])
                        {
                            download = lines[i + 1];
                        }
                    }
                    string localmodellist = localhost("local","");
                    string [] localmodels = localmodellist.Split('\n');
                    if(localmodels.Contains(canshu))
                    {
                        console("red","该模块已经安装在您的产品上了，若需修复模块，请执行卸载更新操作。具体操作请键入help install查看帮助", "The module is already installed on your product. If you need to repair the module, please perform the uninstallation and update operation. For specific instructions, please type help install to view the help");
                        return;
                    }
                    if (download == "")
                    {
                        console("red", "\n无法找到该模块" + canshu, "\nUnable to find the module" + canshu);
                        return;
                    }
                }
                //http-server http path
                string fileUrl = download;
                console("blue", fileUrl, fileUrl);
                string savePath = @"bag\" + canshu + ".dox"; // 保存模块文件的路径
                string extractPath = @"model"; // 解压目标路径

                using (WebClient client = new WebClient())
                {
                    try
                    {
                        // 下载文件
                        client.DownloadFile(fileUrl, savePath);
                        long fileSize = long.Parse(client.ResponseHeaders.Get("Content-Length"));
                        console("", "下载文件" + canshu, "download file " + canshu);
                        console("", "文件大小" + file_size(fileSize.ToString()), "file size " + file_size(fileSize.ToString()));
                        for (int i = 0; i <= 100; i++)
                        {
                            UpdateProgress(i, "green");
                            Thread.Sleep(20); // 模拟操作的延迟
                            Console.ForegroundColor = ConsoleColor.White;
                        }
                        console("green", "文件下载成功！", "File download successful!");

                        console("", "解压模块包", "Decompression module package");
                        ZipFile.ExtractToDirectory(savePath, extractPath);
                        for (int i = 0; i <= 100; i++)
                        {
                            UpdateProgress(i, "blue");
                            Thread.Sleep(10); // 模拟操作的延迟
                            Console.ForegroundColor = ConsoleColor.White;
                        }
                        // 解压文件
                       
                        console("green", "文件解压成功！", "File decompression successful!");
                        console("blue","正在执行Dox优化......", "Performing Dox optimization...");
                        Thread.Sleep(2000);
                        File.Delete(savePath);
                    }
                    catch (Exception ex)
                    {
                        console("red", "\n操作失败：" + ex.Message, "\noperation failed" + ex.Message);
                        console("red", "\n出现未知异常，可能是读取model列表大小失败或文件下载失败\n\n", "\nAn unknown exception occurred, possibly due to a failure to read the model list size or file download failure\n\n");
                        Thread.Sleep(1000);
                        console("red", "正在启动Dox自检...", "Starting Dox self test...");
                        Thread.Sleep(5000);
                        check();
                    }
                }
            }
            else if(sp.Length == 2)
            {
                if (sp[0] == "-u")
                {
                    Thread.Sleep(1000);
                    string[] model_list = localhost("local", "").Split('\n');
                    for (int i = 0; i < model_list.Length; i++)
                    {
                        if (sp[1] == model_list[i])
                        {
                            Directory.Delete("model\\" + sp[1],true);
                            console("green","\n已卸载该模块，欢迎再次使用","");
                            return;
                        }
                    }
                    console("red", "无法卸载模块" + sp[1] + "，原因是未在已安装的模块中找到该模块", "Unable to uninstall module " + sp[1] + " because it was not found in the installed module");
                }
            }
        }
        static string file_size(string bit)//在使用install命令时判断文件大小，并装换成适宜单位，默认输入为字节（B）
        {
            double Bit = int.Parse(bit);
            if (Bit <= 1000)
            {
                return bit + " (B)";
            }
            else
            {
                Bit = Bit / 1024;
                if (Bit <= 1000)
                {
                    return Bit.ToString() + " (KB)";
                }
                else
                {
                    Bit = Bit / 1024;
                    if (Bit <= 1000)
                    {
                        return Bit.ToString() + " (MB)";
                    }
                    else
                    {
                        Bit = Bit / 1024;
                        return Bit.ToString() + " (GB)";
                    }
                }
            }
        }
        static void print(string str)//在控制台输出一些内容
        {
            if (str == "ip")
            {
                Console.Write("\n");
                var interfaces = NetworkInterface.GetAllNetworkInterfaces();
                foreach (var adapter in interfaces)
                {
                    if (adapter.NetworkInterfaceType == NetworkInterfaceType.Ethernet && adapter.OperationalStatus == OperationalStatus.Up)
                    {
                        var ipProperties = adapter.GetIPProperties();
                        foreach (var ipAddress in ipProperties.UnicastAddresses)
                        {
                            if (ipAddress.Address.AddressFamily == AddressFamily.InterNetwork)
                            {
                                Console.WriteLine("{0,-40}" + ipAddress.Address.ToString(), adapter.Name.ToString());
                            }
                        }
                    }
                }
            }
            else if (str == "sys_language")//查询系统当前语言
            {
                Console.WriteLine(lang);
            }
            else if(str == "path")
            {
                path("print_any_path","");
            }
            else
            {
                Console.WriteLine("\n" + str);
            }
        }
        static void time(string str)//获取系统当前的时间
        {
            string lang = localhost("language", "");
            string[] splitted = str.Split(' ');
            if (str == "")
            {
                string time_now = DateTime.Now.ToString();
                console("", "当前系统时间：" + time_now, "Current system time:" + time_now);
            }
        }
        static void cd(string path)//进入新的目录
        {
            if (path == "../" || path == "..\\")
            {
                try
                {
                    DirectoryInfo folderInfo = new DirectoryInfo(quanju);
                    string Parent_Directory = folderInfo.Parent.FullName;
                    quanju = Parent_Directory;
                }
                catch (Exception)
                {
                    console("red", "\ncd：返回上级目录无效无效。", "\ncd: Invalid return to parent directory.");
                }
                return;
            }
            if (path == "\\" || path == "/")
            {
                quanju = Path.GetPathRoot(quanju);//获取路径的盘符
                return;
            }
            if (path == "\\dox")
            {
                quanju = "Dox:";
                return;
            }
            if (path != "")
            {
                if (System.IO.Directory.Exists(path))
                {
                    quanju = path;
                }
                else if (System.IO.Directory.Exists(quanju + "\\" + path))
                {
                    quanju = quanju + "\\" + path;
                }
                else
                {
                    console("red", "cd命令无法将“" + path + "”识别为盘符或驱动器路径", "The cd command cannot recognize '" + path + "' as a drive letter or drive path");
                }
            }
            else
            {
                console("red", "\n你的语法存在错误：“cd”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'cd'?");
            }
        }
        static void dir()//查看当前目录下的所有文件和文件夹
        {
            if (quanju == "Dox:")
            {
                console("red", "dir：当前未选择并进入驱动器以及路径，dir无效。", "dir: Currently, no drive or path has been selected and entered, dir is invalid.");
            }
            else
            {
                if (Path.IsPathRooted(quanju) == true)
                {
                    Console.WriteLine("true");
                }
                try
                {
                    string[] files = Directory.GetFiles(quanju);
                    string[] directories = Directory.GetDirectories(quanju);

                    foreach (string file in files)
                    {
                        FileInfo fileInfo = new FileInfo(file);
                        DateTime lastModified = fileInfo.LastWriteTime;
                        Console.WriteLine("文件(file): {0,-30} 时间(time): {1}", Path.GetFileName(file), lastModified);//格式化字符串输出，保持30字符的间距
                    }

                    foreach (string directory in directories)
                    {
                        DirectoryInfo folderInfo = new DirectoryInfo(directory);
                        DateTime lastModified = folderInfo.LastWriteTime;
                        Console.WriteLine("文件夹(folder): {0,-30} 时间(time): {1}", folderInfo.Name, lastModified);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.Message);
                    console("red", "\n\n\n访问遭到拒绝，请尝试以管理员权限运行Dox", "\n\n\nAccess denied, please try running Dox with administrator privileges");
                    return;
                }
            }
        }
        static void panduan(string bianliang)//主要函数，功能的接口
        {
            string[] splitted = bianliang.Split(' ');
            int i = 0;
            string shuchu = "";
            for (int e = 1; e < splitted.Length; e++)
            {
                if (e == 1)
                {
                    shuchu = splitted[1];
                }
                else if (e > 1)
                {
                    shuchu = shuchu + " " + splitted[e];
                }
            }//提供大多数命令的代码
            if (splitted[i] == "help")
            {
                if (splitted.Length == 1)
                {
                    help("");
                }
                else
                {
                    string shuchu_help = "";
                    for (int e = 1; e < splitted.Length; e++)
                    {
                        shuchu_help += splitted[e];
                    }
                    help(shuchu_help);
                }
            }
            else if (splitted[i] == "show")
            {
                if (splitted.Length == 1 || splitted[1] == "")
                {
                    console("red", "\n你的语法存在错误：“show”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'show'?");
                }
                else
                {
                    string shuchu_show = "";
                    for (int e = 1; e < splitted.Length; e++)
                    {
                        shuchu_show += splitted[e];
                    }
                    show(shuchu_show);
                }
            }
            else if (splitted[i] == "clear")
            {
                Console.Clear();
            }
            else if (splitted[i] == "print")
            {
                //i++;
                if (splitted.Length == 1 || splitted[1] == "")
                {
                    console("red", "\n你的语法存在错误：“print”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'print'?");
                }
                else
                {
                    string shuchu_print = "";
                    for (int e = 1; e < splitted.Length; e++)
                    {
                        shuchu_print += splitted[e];
                    }
                    print(shuchu_print);
                }
            }
            else if (splitted[i] == "set")
            {
                if (splitted.Length == 1 || splitted[1] == "")
                {
                    console("red", "\n你的语法存在错误：“set”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'set'?");
                }
                else
                {
                    string shuchu_set = "";
                    for (int e = 1; e < splitted.Length; e++)
                    {
                        if (e == 1)
                        {
                            shuchu_set = splitted[1];
                        }
                        else if (e > 1)
                        {
                            shuchu_set = shuchu_set + " " + splitted[e];
                        }
                    }
                    set(shuchu_set);
                }
            }
            else if (splitted[i] == "start")
            {
                Console.WriteLine("start:" + shuchu);
                if (splitted[splitted.Length - 1] == "true")
                {
                    try
                    {
                        string[] fdsa = shuchu.Split(' ');
                        if (fdsa.Length > 1)
                        {
                            shuchu = "";
                            for (int e = 0; e < fdsa.Length - 1; e++)
                            {
                                shuchu = shuchu + " " + fdsa[e];
                            }
                        }
                        start_model(shuchu);
                    }
                    catch (Exception e)
                    {
                        Console.WriteLine(e.Message);
                        console("red","\n无法在当前终端打开该参数", "\nUnable to open this parameter on the current terminal");
                    }
                }
                else
                {
                    start(shuchu);
                }
            }
            else if (splitted[i] == "del")
            {
                del(shuchu);
            }
            else if (splitted[i] == "add")
            {
                add(shuchu);
            }
            else if (splitted[i] == "time")
            {
                time(shuchu);
            }
            else if (splitted[i] == "cd")
            {
                cd(shuchu);
            }
            else if (splitted[i] == "dir")
            {
                dir();
            }
            else if (splitted[i] == "install")
            {
                install(shuchu);
            }
            else if (splitted[i] == "check")
            {
                check();
            }
            else if (splitted[i] == "update")
            {
                update();
            }
            else if (splitted[i] == "lock")
            {
                EncryptionHelper.Lock(shuchu);
            }
            else if (splitted[i] == "color")
            {
                color(shuchu);
            }
            else if (splitted[i] =="create")
            {
                create(shuchu);
            }
            else if (splitted[i] == "donghua")
            {
                donghua();
            }
            else if (splitted[i] == "desktop")//快捷进入系统桌面目录
            {
                cd(localpath);
            }
        }
        static void start(string a)//打开
        {
            if (a == "")
            {
                console("red", "\n你的语法存在错误：“start”的后面是否需要一个参数？", "\nThere is an error in your grammar: Do you need a parameter after 'start'?");
                return;
            }
            string str = Environment.CurrentDirectory + "\\model\\" + a + "\\" + a + ".exe";
            try
            {
                string fdsa = path("start",a);//dox系统变量高于一切，包括模块
                if(fdsa == "true")
                {
                    return;
                }
                start_model(str);
            }
            catch (Exception)
            {
                try
                {
                    str = "C:\\Windows\\System32\\" + a + ".exe";//调用system32文件夹下的执行文件
                    Process.Start(str);
                }
                catch (Exception)
                {
                    try
                    {
                        Process.Start(a);//打开网址
                    }
                    catch (Exception)
                    {
                        string path = quanju + "\\" + a;
                        try
                        {
                            if (Directory.Exists(Path.GetDirectoryName(path)))
                            {
                                Process.Start(path);
                            }
                            else
                            {
                                console("red", "start：无法找到“" + a + "”，请确认文件，路径或模块的名字再次尝试。", "start: Unable to find '" + a + "'. Please confirm the file, path, or module name and try again.");
                            }
                            
                        }
                        catch (Exception)
                        {
                            console("red", "start：无法找到“" + a + "”，请确认文件，路径或模块的名字再次尝试。", "start: Unable to find '" + a + "'. Please confirm the file, path, or module name and try again.");
                        }
                    }
                }
            }
        }
        static void start_model(string a)
        {
                Console.WriteLine("");
                Process process = new Process();
                process.StartInfo.FileName = a;
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = false;
                process.StartInfo.RedirectStandardInput = false;
                process.StartInfo.CreateNoWindow = false;
                process.Start();

                // 等待另一个控制台程序结束
                process.WaitForExit();
                Console.WriteLine("\n\n");
        }//启动Dox模块
        static void del(string a)//去掉一些内容
        {
            if (a == "message")
            {
                File.WriteAllText("set\\message", "false");
                console("yellow", "版本提示消息已禁用，可键入“add message”启用提示", "The version prompt message has been disabled. You can type 'add message' to enable the prompt");
            }
            else if(a == "path")
            {
                if (!File.Exists("set/path"))//确保文件存在，哪怕文件为空
                {
                    File.Create("set/path").Close();
                }
                console("blue","\n请输入变量名：", "\nPlease enter a variable name:");
                string delname = Console.ReadLine();
                string allname = File.ReadAllText("set/path");
                if(allname == "")
                {
                    console("red","\npath为空","\npath is null");
                    return;
                }
                string[] names = allname.Split('\n');
                string shuchu = "";
                for (int i = 0;i<names.Length;i++)
                {
                    string[] ab = names[i].Split('&');
                    string one = ab[0];
                    if (one == delname)
                    {
                        string two = ab[1];
                        console("yellow","\n请确认删除该值（n取消）：" + two, "Please confirm to delete the value(n cancelled): " + two);
                        string fdsa = Console.ReadLine();
                        if (fdsa == "n")
                        {
                            return;
                        }
                        continue;
                    }
                    if (names[i] != "")
                    {
                        shuchu = shuchu + names[i] + "\n";
                    }
                    else
                    {
                        shuchu = shuchu + names[i];
                    }
                }
                File.WriteAllText("set/path",shuchu);
            }
            else // 删除文件或目录
            {
                if(a == "" || a == " " || a == "  " || a == "   " || a == "    " || a == "     " || a == "      " || a == "       " || a == "        " || a == "         " || a == "          " || a == "           " || a == "            ")
                {
                    console("red","\n此操作会将目录  " + quanju + "  下的所有文件以及目录删除，是否继续操作(y)", "\\nThis operation will remove the directory  \" + quanju + \"  Delete all files and directories under. Continue with operation (y)");
                    string poiu = Console.ReadLine();
                    if (poiu != "y" && poiu != "Y")
                    {
                        return;
                    }
                }
                string path = Path.Combine(quanju, a);
                try
                {
                    if (File.Exists(path))
                    {
                        File.Delete(path);
                        console("green", "文件删除成功：" + path, "File deleted successfully: " + path);
                    }
                    else if (Directory.Exists(path))
                    {
                        Directory.Delete(path, true);
                        console("green", "目录删除成功：" + path, "Directory deleted successfully: " + path);
                    }
                    else
                    {
                        console("red", "请确认“" + a + "”是一个参数，或者是一个目录或文件名。", "Please confirm that '" + a + "' is a parameter, or a directory or file name.");
                    }
                }
                catch (Exception ex)
                {
                    console("red", "删除文件或目录时发生异常：" + ex.Message, "An exception occurred while deleting the file or directory: " + ex.Message);
                }
            }
        }
        static void add(string a)//增加一些内容
        {
            if (a == "message")
            {
                File.WriteAllText("set\\message", "true");
                console("red", "版本提示消息已启用，可键入“del message”禁用用提示", "Version prompt message enabled, you can type 'del message' to disable the prompt");
            }
            else if (a == "path")
            {
                console("blue", "请输入变量名（&的前面）和变量值（&的后面）", "Please enter the variable name (before&) and variable value (after&)");
                string path = Console.ReadLine();
                
                int index = path.IndexOf("&");

                if (index >= 0 && path.IndexOf("&", index + 1) < 0)
                {
                    string[] aaa = path.Split('&');
                    if (aaa[0] == "" || aaa[1] == "")
                    {
                        console("red","\n输入的值不合法：（&）的前面和后面不能为空", "\nThe entered value is illegal: the front and back of (&) cannot be empty");
                    }
                    else
                    {
                        using (StreamWriter writer = File.AppendText("set/path"))
                        {
                            writer.WriteLine(path);
                        }
                        console("green","创建系统变量成功！", "Successfully created system variable!");
                    }
                }
                else
                {
                    console("red","\n字符串不合法：字符串应该包含有且只有一个（&）", "\nIllegal string: The string should contain and only have one (&)");
                }
            }
        }
        static void create(string a)//创建一些内容，包括目录和文件
        {
            string[] sp = a.Split('&');
            //create file filename savepath true/false/null
            //create dir dir_name savepath true/false/null
            if (sp.Length < 4)
            {
                console("red", "\ncreate：缺少必要参数\ncreate(string style, string name, string savepath, string true_or_false)", "\ncreate: Required parameter missing\ncreate(string style, string name, string savepath, string true_or_false)");
                return;
            }
            else if (sp.Length > 4)
            {
                console("red", "\ncreate：该命令仅接收四个参数", "\ncreate: This command only accepts four parameters");
                return;
            }

            try
            {
                if (sp[0] == "file")
                {
                    string filePath;
                    string fileName = sp[1];
                    string savePath = sp[2];

                    // 检查savepath是否包含文件名
                    if (Path.GetFileName(savePath) == savePath)
                    {
                        // savepath只包含目录路径，需要拼接文件名
                        filePath = Path.Combine(savePath, fileName);
                    }
                    else
                    {
                        // savepath已经包含了完整的文件路径，直接使用
                        filePath = savePath;
                    }

                    if (File.Exists(filePath))
                    {
                        if (sp[3].ToLower() == "true")
                        {
                            File.Delete(filePath);
                            File.Create(filePath).Close();
                            console("green", "\n文件已存在，已成功删除并重新创建：" + filePath, "\nThe file already exists, it has been successfully deleted and recreated: " + filePath);
                        }
                        else if (sp[3].ToLower() == "false")
                        {
                            console("red", "\n文件已存在，创建失败：" + filePath, "\nThe file already exists, creation failed: " + filePath);
                        }
                        else if (sp[3].ToLower() == null)
                        {
                            console("yellow", "\n文件已存在，使用默认行为：" + filePath, "\nThe file already exists, using default behavior: " + filePath);
                        }
                    }
                    else
                    {
                        File.Create(filePath).Close();
                        console("green", "\n文件创建成功：" + filePath, "\nFile created successfully: " + filePath);
                    }
                }
                else if (sp[0] == "dir")
                {
                    string dirPath;
                    string dirName = sp[1];
                    string savePath = sp[2];

                    // 检查savepath是否包含目录名
                    if (Path.GetFileName(savePath) == savePath)
                    {
                        // savepath只包含父级目录路径，需要拼接目录名
                        dirPath = Path.Combine(savePath, dirName);
                    }
                    else
                    {
                        // savepath已经包含了完整的目录路径，直接使用
                        dirPath = savePath;
                    }

                    if (Directory.Exists(dirPath))
                    {
                        if (sp[3].ToLower() == "true")
                        {
                            Directory.Delete(dirPath, true);
                            Directory.CreateDirectory(dirPath);
                            console("green", "\n目录已存在，已成功删除并重新创建：" + dirPath, "\nThe directory already exists, it has been successfully deleted and recreated: " + dirPath);
                        }
                        else if (sp[3].ToLower() == "false")
                        {
                            console("red", "\n目录已存在，创建失败：" + dirPath, "\nThe directory already exists, creation failed: " + dirPath);
                        }
                        else if (sp[3].ToLower() == null)
                        {
                            console("yellow", "\n目录已存在，使用默认行为：" + dirPath, "\nThe directory already exists, using default behavior: " + dirPath);
                        }
                    }
                    else
                    {
                        Directory.CreateDirectory(dirPath);
                        console("green", "\n目录创建成功：" + dirPath, "\nDirectory created successfully: " + dirPath);
                    }
                }
                else
                {
                    console("red", "\ncreate：无法识别的类型 ”" + sp[0] + "“", "\ncreate：Unrecognized type ”" + sp[0] + "“");
                }
            }
            catch (Exception ex)
            {
                console("red", "\ncreate：发生异常：" + ex.Message, "\ncreate: An exception occurred: " + ex.Message);
            }
        }
        static void color(string a)//设置Dox的主题颜色
        {
            string[] sp = a.Split(' ');
            if (sp.Length != 2)
            {
                console("red","\ncolor：您的语法存在错误，color的后面是否存在两个参数？", "Color: There is an error in your syntax. Are there two parameters after color?");
                return;
            }
            console("red","更改Dox样式会清除屏幕已缓存的内容，请谨慎操作。您的操作可能会导致某些操作的渲染不美观，建议您使用默认样式捏", "Changing the Dox style will clear the cached content on the screen, please be cautious. Your actions may result in unsightly rendering of certain actions. It is recommended that you use the default style of pinching");
            console("blue","回车执行（输入小写n取消操作）", "Enter to execute (enter lowercase n to cancel the operation)");
            string fdsa = Console.ReadLine();
            if(fdsa == "n")
            {
                return;
            }
            string color = sp[0].ToLower();

            switch (color)
            {
                case "black":
                    Console.BackgroundColor = ConsoleColor.Black;
                    break;
                case "white":
                    Console.BackgroundColor = ConsoleColor.White;
                    break;
                case "green":
                    Console.BackgroundColor = ConsoleColor.Green;
                    break;
                case "red":
                    Console.BackgroundColor = ConsoleColor.Red;
                    break;
                case "yellow":
                    Console.BackgroundColor = ConsoleColor.Yellow;
                    break;
                case "blue":
                    Console.BackgroundColor = ConsoleColor.Blue;
                    break;
                case "magenta":
                    Console.BackgroundColor = ConsoleColor.Magenta;
                    break;
                case "cyan":
                    Console.BackgroundColor = ConsoleColor.Cyan;
                    break;
                case "darkblue":
                    Console.BackgroundColor = ConsoleColor.DarkBlue;
                    break;
                case "darkcyan":
                    Console.BackgroundColor = ConsoleColor.DarkCyan;
                    break;
                case "darkgray":
                    Console.BackgroundColor = ConsoleColor.DarkGray;
                    break;
                case "darkgreen":
                    Console.BackgroundColor = ConsoleColor.DarkGreen;
                    break;
                case "darkmagenta":
                    Console.BackgroundColor = ConsoleColor.DarkMagenta;
                    break;
                case "gray":
                    Console.BackgroundColor = ConsoleColor.Gray;
                    break;
                case "darkred":
                    Console.BackgroundColor = ConsoleColor.DarkRed;
                    break;
                case "darkyellow":
                    Console.BackgroundColor = ConsoleColor.DarkYellow;
                    break;
                default:
                    Console.WriteLine("Invalid color.");
                    break;
            }

            string color1 = sp[1].ToLower();

            switch (color1)
            {
                case "black":
                    Console.ForegroundColor = ConsoleColor.Black;
                    break;
                case "white":
                    Console.ForegroundColor = ConsoleColor.White;
                    break;
                case "green":
                    Console.ForegroundColor = ConsoleColor.Green;
                    break;
                case "red":
                    Console.ForegroundColor = ConsoleColor.Red;
                    break;
                case "yellow":
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    break;
                case "blue":
                    Console.ForegroundColor = ConsoleColor.Blue;
                    break;
                case "magenta":
                    Console.ForegroundColor = ConsoleColor.Magenta;
                    break;
                case "cyan":
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    break;
                case "darkblue":
                    Console.ForegroundColor = ConsoleColor.DarkBlue;
                    break;
                case "darkcyan":
                    Console.ForegroundColor = ConsoleColor.DarkCyan;
                    break;
                case "darkgray":
                    Console.ForegroundColor = ConsoleColor.DarkGray;
                    break;
                case "darkgreen":
                    Console.ForegroundColor = ConsoleColor.DarkGreen;
                    break;
                case "darkmagenta":
                    Console.ForegroundColor = ConsoleColor.DarkMagenta;
                    break;
                case "gray":
                    Console.ForegroundColor = ConsoleColor.Gray;
                    break;
                case "darkred":
                    Console.ForegroundColor = ConsoleColor.DarkRed;
                    break;
                case "darkyellow":
                    Console.ForegroundColor = ConsoleColor.DarkYellow;
                    break;
                default:
                    Console.WriteLine("Invalid color.");
                    return;
            }
            Console.Clear();
        }
        static void donghua()//开机动画，add message开启
        {
            string text = File.ReadAllText("set\\animation");
            char[] chars = text.ToCharArray();
            for (int i = 0; i < chars.Length; i++)
            {
                try
                {
                    Random random = new Random();
                    for (int z = 0; z < 20; z++)
                    {
                        int a = random.Next(4);
                        if (a == 0)
                        {
                            Console.ForegroundColor = ConsoleColor.Red;
                        }
                        else if (a == 1)
                        {
                            Console.ForegroundColor = ConsoleColor.Green;
                        }
                        else if (a == 2)
                        {
                            Console.ForegroundColor = ConsoleColor.Blue;
                        }
                        else
                        {
                            Console.ForegroundColor = ConsoleColor.Yellow;
                        }
                        Console.Write(chars[i + z]);
                    }
                    i = i + 19;
                    Thread.Sleep(20);
                }
                catch
                {

                }
            }
            Console.ForegroundColor = ConsoleColor.White;
        }
        static string path(string style, string str)//Dox系统环境变量
        {
            if (!File.Exists("set/path"))
            {
                File.Create("set/path").Close();
            }
            if (style == "print_any_path")
            {
                string paths = File.ReadAllText("set/path");
                if (paths != "")
                {
                    Console.WriteLine();
                    console("blue",paths,paths);
                }
                else
                {
                    console("yellow","系统变量为空","system path is null");
                }
                return "";
            }
            else if(style == "start")
            {
                string paths = File.ReadAllText("set/path");
                if(paths != "")
                {
                    string[] pathss = paths.Split('\n');
                    string a = "";
                    string b = "";
                    string boool = "false";
                    for(int i = 0; i < pathss.Length; i++)
                    {
                        if (pathss[i] == "")
                        {
                            break;
                        }
                        string[] aaa = pathss[i].Split('&');
                        a = aaa[0];
                        b = aaa[1];
                        if(str == a)
                        {
                            start(b);
                            boool = "true";
                            break;
                        }
                    }

                    return boool;
                }
            }
            return "";
        }
        static void first()
        {
            try
            {
                Console.OutputEncoding = System.Text.Encoding.UTF8;
            }
            catch (Exception)
            {
                MessageBox.Show("Dox的文字编码初始化错误，请联系开发者Yunqingli", "初始化错误");
            }
            
            //判断Dox是否初次启动
            string pan = File.ReadAllText("set\\first");
            if (pan == "false")
            {

                Thread.Sleep(2000);
                Console.Clear();


                console("blue", "您的Dox初次启动，我们需要为您配置一些内容，以优化您的使用体验", "Your Dox is starting for the first time, and we need to configure some content for you to optimize your user experience");
                Thread.Sleep(6000);
                Console.Clear();
                console("blue", "这个内容包括配置您的密钥，创建必要的数据文件目录，检查Dox的完整性，安装必要的帮助文档", "This content includes configuring your key, creating necessary data file directories, checking the integrity of Dox, and installing necessary help documents");
                Thread.Sleep(6000);
                Console.Clear();
                console("blue", "此操作不需要您在互联网环境下", "This operation does not require you to be in an internet environment");
                Thread.Sleep(6000);
                Console.Clear();
                console("blue", "等待开始", "waiting to start");
                Thread.Sleep(5000);
                Console.Clear();


                int fdas = 0;
                for (int i = 0; i < 10; i++)
                {
                    fdas += 10;
                    Console.Clear();
                    Console.WriteLine("Dox初始化 加载中    " + " (" + fdas.ToString() + "%) ");
                    Thread.Sleep(500);
                    Console.Clear();
                    Console.WriteLine("Dox初始化 加载中.   " + " (" + fdas.ToString() + "%) ");
                    Thread.Sleep(500);
                    Console.Clear();
                    Console.WriteLine("Dox初始化 加载中..  " + " (" + fdas.ToString() + "%) ");
                    Thread.Sleep(500);
                    Console.Clear();
                    Console.WriteLine("Dox初始化 加载中... " + " (" + fdas.ToString() + "%) ");
                    Thread.Sleep(500);
                    Console.Clear();
                    Console.WriteLine("Dox初始化 加载中...." + " (" + fdas.ToString() + "%) ");
                    Thread.Sleep(500);
                }
                Thread.Sleep(2000);
                Console.Clear();
                Thread.Sleep(1000);
                Console.WriteLine("配置您的密匙ing");
                Thread.Sleep(1000);
                Thread.Sleep(500);
                Console.Clear();
                Console.WriteLine("即将完成");
                Thread.Sleep(5000);
                Console.Clear();
                Thread.Sleep(2000);
                Thread.Sleep(3000);
                Console.Clear();
                File.WriteAllText("set\\first", "true");
                File.WriteAllText("set\\message", "true");
            }

            try
            {
                string line = File.ReadAllText("set/message");
                if (line == "true")
                {
                    donghua();
                    Thread.Sleep(2000);
                    Console.Clear();
                    Console.Beep();
                }

                Console.WriteLine(lang);
            }
            catch (Exception)
            {
                MessageBox.Show("Dox初始化文件失效，文件缺失\n\nNot file 'message'!", "文件缺失");
                Environment.Exit(0);
            }
            //强调版本号
            File.WriteAllText("version", "1.0.0.0");
        }//初始化函数，开启个别功能的线程
        static void UpdateProgress(float progress, string color)
        {
            Console.CursorLeft = 0;
            Console.Write("| ");
            Console.CursorLeft = 32;
            Console.Write(" |");
            Console.CursorLeft = 1;
            float onechunk = 30.0f / 100;

            int position = 1;
            for (int i = 0; i < onechunk * progress; i++)
            {
                Console.CursorLeft = position++;
                if (color == "red")
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                }
                if (color == "green")
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                }
                if (color == "blue")
                {
                    Console.ForegroundColor = ConsoleColor.Blue;
                }
                if (color == "yellow")
                {
                    Console.ForegroundColor = ConsoleColor.Yellow;
                }
                Console.Write("─");
            }

            Console.CursorLeft = 35;
        }//进度条
        /*
         for (int i = 0; i <= 100; i++)
            {
                UpdateProgress(i);
                Thread.Sleep(100); // 模拟操作的延迟
                Console.ForegroundColor = ConsoleColor.White;
            }
         */
        //进度条调用
        static void Main(string[] args)//Dox的主函数
        {
            first();//初始化
            string bianliang = "";
            console("", "云清璃 Dox [版本 1.0.0000.00.0]\n(c) 云清璃出品。保留所有权利。\n", "Yunqingli Dox [Version 1.0.0000.00.0]\n(c) Produced by Yunqingli. All right reserved. \n");

            do
            {
                bianliang = "";//用于时刻获取用户的输入
                Console.Write("\n" + quanju + " \U0001F600💖>");
                try
                {
                    bianliang = Console.ReadLine();
                    bianliang = bianliang.ToLower(CultureInfo.CurrentCulture);
                }
                catch (Exception ex)
                {
                    Console.Write("\n" + ex.Message);
                    console("red", "\n异常的输入，请确保复制的文本大小不大于string的长度", "\nAbnormal input, please ensure that the copied text size is not greater than the length of the string");
                }
                if (bianliang == "exit(1)")//重启
                {
                    System.Diagnostics.Process.Start(Application.ExecutablePath);
                    Environment.Exit(0);
                }

                string beifen = quanju;
                panduan(bianliang);
                try
                {
                    if (quanju != "Dox:")
                    {
                        quanju = Path.GetFullPath(quanju);
                    }
                }
                catch (Exception)
                {
                    console("red", "\ncd：返回根目录无效", "\ncd: Invalid return root directory");
                    quanju = beifen;
                }
                //zijian();
            }
            while (bianliang != "exit" && bianliang != "exit(0)");
        }
    }

}

//表情
/*
 笑脸表情：

😀 😃 😄 😁 😆 😊 😎
爱心表情：

❤️ 💕 💖 💘 💓 💗 💞
笑泪表情：

😂 🤣 😅 😆
惊讶表情：

😮 😲 😯 😱
难过表情：

😔 😢 😭 😞 😟
生气表情：

😡 😠 😤 💢
眨眼表情：

😉 😜 😝 😏
鼓掌表情：

👏 🙌 🎉 🎊
看不见表情：

👀 🙈 🙉 🙊
睡觉表情：

😴 💤
 */