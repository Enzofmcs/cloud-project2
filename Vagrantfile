Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "projeto2-cloud"
    vb.cpus = 2
    vb.memory = 4096
  end

  # Acesse a web pela 8080 no host (Apache) e 5000 (Flask direto)
  config.vm.network "forwarded_port", guest: 80, host: 8080, auto_correct: true
  config.vm.network "forwarded_port", guest: 5000, host: 5000, auto_correct: true

  # Sincroniza pasta do projeto para /vagrant (padrão)
  config.vm.synced_folder ".", "/vagrant"

  # Provisiona tudo
  config.vm.provision "shell", path: "provision.sh"
end
