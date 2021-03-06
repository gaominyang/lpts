
#!/bin/bash
# set -x

#传递参数为要执行的机器parameter
# set parame [lindex $argv 0]

#进入执行目录
sleep 600
chmod 777 /etc/rc.d/rc.local
cd  /home/lpts-3.10.0
for line in $(cat flag.txt)
do
       echo $line;
       if [ $line -eq "1" ]; then
       	echo "/bin/bash  /home/lpts-3.10.0/reboot.sh"  >>  /etc/rc.d/rc.local 
              ./lpts.py --create -t stream -f  jobs.xml -p parameters/$parame -n testname > /opt/stream.txt 2>&1
		echo $?
		./lpts.py --run -t stream -f jobs.xml >>/opt/stream.txt 2>&1
		echo $?
              echo "2" >flag.txt
              reboot   
       elif [ $line -eq "2" ]; then
            	./lpts.py --create -t unixbench -f  jobs.xml -p parameters/$parame -n testname > /opt/unixbench.txt 2>&1
		echo $?
		./lpts.py --run -t unixbench -f jobs.xml >>/opt/unixbench.txt 2>&1
		echo $?
              echo "3" >flag.txt
		reboot
	elif [ $line -eq "3" ]; then
		echo $line
		./lpts.py --create -t x11perf -f  jobs.xml -p parameters/$parame  -n testname > /opt/x11perf.txt 2>&1
		echo $?
		./lpts.py --run -t x11perf -f jobs.xml >>/opt/x11perf.txt 2>&1
		echo "4" >flag.txt
		reboot
	elif [ $line -eq "4" ]; then
              ./lpts.py --create -t pingpong -f  jobs.xml -p parameters/$parame  -n testname > /opt/pingpong.txt 2>&1
              echo $?
              ./lpts.py --run -t pingpong  -f jobs.xml >>/opt/pingpong.txt 2>&1
		echo $?
              echo "5" >flag.txt
		reboot
	elif [ $line -eq "5" ]; then
              	mem_total=`free |  grep Mem | awk '{print $2}'`
		mem_1=$(expr $mem_total + 512000)
		echo $mem_1
		num2=1024000
		mem_e=`echo "sclae=0; $mem_1/$num2" | bc` 

		for line_iozone in $(cat iozone_flag.txt)
		do
			if [ $line_iozone -eq "0" ]; then
				mem_i=`echo "sclae=0; $mem_e/2" | bc` 
				echo "1" >iozone_flag.txt
				echo "5" >flag.txt
			elif [ $line_iozone -eq "1" ]; then
				mem_i=$mem_e
				echo "2" >iozone_flag.txt
				echo "5" >flag.txt
			elif [ $line_iozone -eq "2" ]; then
				mem_i=$(expr $mem_e \* 2)
				echo "0" >iozone_flag.txt
				echo "6" >flag.txt
			fi
		done

		str1="64c FILESIZE  = $mem_i"
		str2="g"
		sed -i "$str1$str2" parameters/$parame
		./lpts.py --create -t iozone -f  jobs.xml -p parameters/$parame  -n testname > /opt/iozone.txt 2>&1
		echo $?
		./lpts.py --run -t iozone -f jobs.xml >>/opt/iozone.txt 2>&1
		echo $?
   
		reboot
	elif [ $line -eq "6" ]; then
              ./lpts.py --create -t bonnie -f  jobs.xml -p parameters/$parame -n testname > /opt/bonnie.txt 2>&1
              echo $?
              ./lpts.py --run -t bonnie -f jobs.xml >>/opt/bonnie.txt 2>&1
		echo $?
              echo "7" >flag.txt
		reboot
	elif [ $line -eq "7" ]; then
       	./lpts.py --create -t dbench_fio -f  jobs.xml -p parameters/$parame  -n testname > /opt/dbench_fio.txt 2>&1
       	echo $?
        	./lpts.py --run -t dbench_fio -f jobs.xml >>/opt/dbench_fio.txt 2>&1
		echo $?
       	echo "8" >flag.txt
		reboot
	elif [ $line -eq "8" ]; then
        	./lpts.py --create -t lmbench -f  jobs.xml -p parameters/$parame  -n testname > /opt/lmbench.txt 2>&1
        	echo $?
        	./lpts.py --run -t lmbench -f jobs.xml >>/opt/lmbench.txt 2>&1
       	echo $?
        	echo "9" >flag.txt
       fi
done


