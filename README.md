# I2C demo
## 关于文件
I2C_RAW是从OpenCore上下载的原始文件
I2C_DIY是我自己修改过的ModelSim工程文件
## 关于I2C
**Inter Integrated Circuit** 简称I2C，本质上是一种通信协议。当说起通信，最简单的办法就是一根数据线，将发送者与接收者连接起来。
<center>
<img src="/../images/posts/I2C/intro1.png" width = "600" alt="基本通信模型" />
Fig 1. 基本通信模型
</center>
这样做的问题在与两边的时钟频率可能不一致，从而导致数据收发不同步。对应的改进措施就是额外使用一条时钟连线，将发送者与接收者的时钟信号进行同步。
<center>
<img src="/../images/posts/I2C/intro2.png" width = "600" alt="改进通信模型" />
Fig 2. 改进通信模型
</center>
这样只要发送者按照约定的时钟频率来发送，接收者按照约定的频率来接收，两边设备就可以正常进行通信。实际上I2C通讯协议就是这样做的，只不过将我们前面提到的发送者与接收者起了特别的名字。
<center>
<img src="/../images/posts/I2C/intro3.png" width = "600" alt="I2C通信模型" />
Fig 3. I2C通信模型
</center>
但是这样的通讯结构依旧有问题，就是只能实现点对点的通信，随着多个设备的加入，连线的复杂程度为O(n^2)。因此I2C引入了总线结构，让上面的SCL、SDA两跟线变成总线，所有设备的通信信号都从这两个线上传输。因此产生下面结构：
<center>
<img src="/../images/posts/I2C/intro4.png" width = "600" alt="I2C总线模型" />
Fig 4. I2C总线模型
</center>
总线结构由于共用了数据线与时钟线，因此为保证正常的通信过程，需要制定一套通信规则。以Master向Servant写入数据的过程为例，I2C的通信过程可以分为以下几个阶段：
1. 产生开始信号
2. 传输Servant ID + Write bit/Read bit(确定是写入还是读取)，接收到Servant的确认信号(acknoledge)之后进入下一步
3. 传输写入Servant的reg address，接收到Servant的确认信号之后进入下一步
4. 传输要写入的数据，并检测Servant的确认信号(每一段数据写完之后都要检查ack信号)
5. 产生结束信号
上述过程可以用以下状态流程图来表示：
<center>
<img src="/../images/posts/I2C/state_diagram.png" width = "800" alt="状态流程图" />
Fig 5. 状态流程图
</center>
而完整的写入过程SDA、SCL时序示意图如下所示:
<center>
<img src="/../images/posts/I2C/timeline.png" width = "1000" alt="时序示意图" />
Fig 6. 时序示意图
</center>
根据OpenCore可以下载到的I2C IP文件，可以在ModelSim中观看到更加真实的I2C工作时序。该IP的Test Bench结构示意图如下：
<center>
<img src="/../images/posts/I2C/testbench.png" width = "1000" alt="Test Bench结构示意图" />
Fig 7. Test Bench结构示意图
</center>
其中wb_master_model是对i2c_master_model的控制单元，产生控制信号，对master进行初始化及读写操作，并选择由哪个master来产生信号。i2c_master_model就是基本I2C模块，接受上层模块产生的控制字，并在I2C总线中产生相应的信号。而i2c_slave_model是一个单纯的servant模块，其不能产生scl信号，只能被动接受SCL与SDA的信号，并在需要进行相应的时候产生ack信号，或传出被读取的信号。slave模型中包含一个深度8bit，高度为4的寄存器阵列，可以存储master写入的数据。
对上述Test Bench仿真产生的时序如下：
<center>
<img src="/../images/posts/I2C/simulation.png" width = "1400" alt="时序仿真图" />
Fig 8. 时序仿真图
</center>
上述的时序完成了以下几个操作：
1. 对master模块进行初始化
2. 产生Start信号(SCL为高时SDA下降)
3. 传输Servant ID + Write bit --> 被Servant接受ack
4. 传输reg address --> ack
5. 传输write数据 --> ack
6. 传输read数据 --> ack
7. 产生Stop信号
Test Bench中的各个过程都进行了标注。初始化过程运行在外部时钟频率下，因此很快就完成了，在波形中只占非常小的一部分。并且可以看到在波形大概五分之一的位置出有一段等待，这里时一个人为的分割，在此信号之后传输的都是数据信号。
最后，自己在OpenCore的IP基础之上进行了一些小的修改，将原来I2C的8bit Servant ID，8bit reg address和8bit 数据信号统统改成了16bit，完成了一个自定义的I2C通信模块，并在Test Bench中把Slave model 也变成了两个。该编之后的仿真波形图如下：
<center>
<img src="/../images/posts/I2C/simulation2.png" width = "1400" alt="改写之后的时序" />
Fig 9. 改写之后的时序
</center>
此时半边的波形为对一号Slave写信息的，右半边波形对二号Slave写信息。
## 后记
该项目除了信号仿真，还进行了综合布线等后端工作，但是这部分工作主要关注于熟悉软件，熟悉数字集成电路的开发流程，并没有什么有新意的内容，因此不做展示。