<template>
  <div>
    <div class="ml-[10px] p-[8px] mt-[2rem]" data-step-content-idx="0">
      <div
        class="centered-column p-well space-y-well bg-accent rounded-md border border-default"
      >
        <div v-if="loaded">
          <div
            v-if="codeGenrated"
            class="text-lg flex flex-col items-center justify-center text-center p-6"
          >
            <p class="mb-2 font-bold">
              Your account has been set up for 2FA. To remove 2FA, click on the button
              below.
            </p>
            <p class="mb-4 text-base">To reset 2FA, you must remove it first.</p>

            <button
              class="bg-red-600 hover:bg-red-700 mt-[2rem] text-white font-semibold py-2 px-4 rounded shadow"
              @click="confirmRemove()"
            >
              Remove 2FA
            </button>
          </div>

          <div v-else>
            <div class="text-center">
              <h2 class="text-2xl font-bold text-default">
                Secure Your Account with Two-Factor Authentication (2FA)
              </h2>
              <p class="mt-2 text-default text-base">
                To get started, install the <strong>Google Authenticator</strong> app on
                your phone:
                <br />
                <a
                  href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                  target="_blank"
                  class="text-blue-500 underline hover:text-blue-700"
                  >Google Play</a
                >
                |
                <a
                  href="https://apps.apple.com/app/google-authenticator/id388497605"
                  target="_blank"
                  class="text-blue-500 underline hover:text-blue-700"
                  >App Store</a
                >
              </p>
            </div>

            <div class="text-center text-default">
              <p class="text-base">
                Once the app is installed, click
                <strong>"Generate QR Code"</strong> below to begin setup.
              </p>
            </div>

            <div
              class="flex flex-col lg:flex-row justify-center items-start gap-12 mt-[5rem]"
            >
              <!-- QR and input -->
              <div class="flex flex-col items-center space-y-4">
                <qrcode-vue
                  v-if="otpUri.length > 0"
                  :value="otpUri"
                  :size="250"
                  class="border-2 border-gray-300 p-2 rounded"
                />

                <div v-if="generateQrBtnClicked" class="text-center space-y-3">
                  <p class="text-bash font-semibold">Can’t scan the QR code?</p>
                  <p class="text-sm text-default">Enter this info manually in the app:</p>

                  <p class="text-sm"><strong>Account:</strong> {{ accountName }}</p>
                  <p class="text-sm break-all font-mono ml-[5rem]">
                    <strong>Key:</strong> {{ secret }}
                  </p>
                  <p class="text-sm">Set type to <strong>Time-based</strong></p>
                </div>

                <div v-if="!generateQrBtnClicked">
                  <button class="btn btn-primary" @click="createAuth()">
                    Generate QR Code
                  </button>
                </div>
                <div v-if="generateQrBtnClicked" class="text-center mt-6">
                  <p class="font-medium">
                    Enter the 6-digit code from your Authenticator app:
                  </p>
                  <input
                    v-model="userInput"
                    type="text"
                    maxlength="6"
                    placeholder="123456"
                    class="mt-2 px-4 py-2 w-40 border mr-[1rem] bg-default border-gray-300 rounded text-center font-mono text-lg tracking-widest"
                  />
                  <button @click="verifyCode(userInput)" class="btn btn-primary mt-4">
                    Verify & Finalize 2FA
                  </button>
                </div>
              </div>
              <!-- Scratch Codes -->
              <div v-if="scratchCodes.length > 0" class="max-w-md w-full">
                <p class="font-bold text-lg mb-2">Emergency Scratch Codes</p>
                <p class="text-bash mb-4">
                  Store these codes in a safe place. Each code can be used once if you
                  lose access to your device.
                </p>
                <ul class="grid grid-cols-2 gap-3 text-red-600 font-mono text-base">
                  <li
                    v-for="(code, index) in scratchCodes"
                    :key="index"
                    class="bg-white border rounded p-2 text-center"
                  >
                    {{ code }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QrcodeVue from "qrcode.vue";
import { Command, legacy } from "@45drives/houston-common-lib";
import { onMounted, ref } from "vue";
import { server } from "@45drives/houston-common-lib";

const otpUri = ref("");
const secret = ref("");
const scratchCodes = ref<string[]>([]);
const codeGenrated = ref(false);
const loaded = ref(false);
const generateQrBtnClicked = ref(false);
const userInput = ref("");
const accountName = ref("");
checkExist().then(() => {
  loaded.value = true;
});

async function checkExist() {
  try {
    const result = await server.execute(
      new Command(["sh", "-c", "cat ~/.google_authenticator"]),
      true
    );

    const output = result.value.getStdout().trim(); // Trim to remove newlines/spaces
    if (output.length > 0) {
      codeGenrated.value = true;
      console.log(" File exists and contains content");
      return true;
    } else {
      codeGenrated.value = false;

      console.warn("⚠️ File is empty or does not contain useful data");
      return false;
    }
  } catch (error) {
    codeGenrated.value = false;

    console.error("❌ Failed to read .google_authenticator file:", error);
    return false;
  }
}

async function generateFile() {
  const result = await server.execute(
    new Command([
      "python3",
      "/opt/45drives/houston/2fa/scripts/generateAuthFIle.py",
      secret.value,
    ]),
    true
  );

  const stdout = new TextDecoder().decode(result.value.stdout).trim();
  const res = JSON.parse(stdout);

  if (res.status === "success") {
    scratchCodes.value = res.scratch_codes;
    alert("✅ 2FA enabled. Save your recovery codes.");
  } else {
    alert("❌ Failed: " + res.message);
  }
}

async function verifyCode(userInput) {
  try {
    const result = await server.execute(
      new Command([
        "python3",
        "/opt/45drives/houston/2fa/scripts/verifyCode.py",
        userInput,
        secret.value,
      ]),
      true
    );

    const stdout = new TextDecoder().decode(result.value.stdout).trim();
    console.log("result", stdout);

    // Try parsing JSON output from the script
    const res = JSON.parse(stdout);

    if (res.status === "valid") {
      // ✅ TOTP is correct
      alert("✅ 2FA code verified successfully!");
      console.log("secret value, ", secret.value);
      generateFile();
      // TODO: call backend to save `.google_authenticator` file or mark setup complete
    } else if (res.status === "invalid") {
      alert("❌ Invalid 2FA code. Please try again.");
    } else {
      alert("⚠️ Verification error: " + (res.message || "Unknown issue."));
    }
  } catch (error) {
    console.error("❌ Error verifying TOTP:", error);
    alert("An error occurred during verification.");
  }
}

async function createAuth() {
  try {
    const result = await server.execute(
      new Command(["python3", "/opt/45drives/houston/2fa/scripts/generateUri.py"]),
      true
    );
    const stdout = new TextDecoder().decode(result.value.stdout);
    console.log("result", stdout);
    const json = JSON.parse(stdout);

    // Access the parsed values
    otpUri.value = json.otpauth_uri;
    secret.value = json.secret;
    accountName.value = json.account;
    generateQrBtnClicked.value = true;
  } catch (e) {
    console.error("❌ Failed to generate OTP:", e);
  }
}

function confirmRemove() {
  if (confirm("Are you sure you want to remove 2FA for this account?")) {
    remove2FA();
  }
}

async function remove2FA() {
  const result = await server.execute(
    new Command(["sh", "-c", "rm -f ~/.google_authenticator"]),
    true
  );
  codeGenrated.value = false;
}
</script>
