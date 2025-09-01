.PHONY: setup run test package-macos clean

setup:
	bash scripts/bootstrap.sh

run:
	bash scripts/run.sh

test:
	bash scripts/test.sh

package-macos:
	cd desktop/electron && npm install && npx electron-builder --mac dmg

clean:
	rm -rf .venv dist build desktop/electron/dist


package-macos-universal:
	cd desktop/electron && npm install && npx electron-builder --mac universal
