sudo apt-get update
sudo apt-get install -y libcairo2-dev libjpeg-turbo8-dev libpng-dev libtool-bin libossp-uuid-dev libavcodec-dev libavutil-dev libswscale-dev freerdp2-dev libpango1.0-dev libssh2-1-dev libtelnet-dev libvncserver-dev libpulse-dev libssl-dev libvorbis-dev libwebp-dev wget maven tomcat9 tomcat9-admin

cd /tmp/
wget https://downloads.apache.org/guacamole/1.5.1/source/guacamole-server-1.5.1.tar.gz
wget https://downloads.apache.org/guacamole/1.5.1/binary/guacamole-1.5.1.war
wget https://downloads.apache.org/guacamole/1.5.1/binary/guacamole-auth-jdbc-1.5.1.jar


tar -xzf guacamole-server-1.5.1.tar.gz
cd guacamole-server-1.5.1
./configure --with-init-dir=/etc/init.d
make
sudo make install
sudo ldconfig
sudo systemctl enable guacd
sudo systemctl start guacd

sudo mkdir /etc/guacamole
sudo mv /tmp/guacamole-1.5.1.war /etc/guacamole/guacamole.war
sudo ln -s /etc/guacamole/guacamole.war /var/lib/tomcat9/webapps/
sudo mkdir /etc/guacamole/{extensions,lib}
sudo mv /tmp/guacamole-auth-jdbc-1.5.1.jar /etc/guacamole/extensions/
sudo wget -O /etc/guacamole/lib/postgresql.jar https://jdbc.postgresql.org/download/postgresql-42.2.23.jar


sudo echo "
guacd-hostname: localhost
guacd-port: 4822
mysql-hostname: localhost
mysql-port: 3306
mysql-database: osi
mysql-username: osi
mysql-password: osi" >> /etc/guacamole/guacamole.properties

sudo mv server.xml /etc/tomcat9/server.xml


sudo systemctl restart tomcat9

curl http://localhost:8080/guacamole/ 