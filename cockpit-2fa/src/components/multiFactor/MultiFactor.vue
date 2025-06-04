<template>
  <div>
    <div class="ml-[10px] p-[8px] mt-[2rem]" data-step-content-idx="0">
      <div
        class="centered-column p-well space-y-well bg-accent rounded-md border border-default">

        <div v-if="loaded">
          <div v-if="codeGenrated" class="text-lg flex flex-col items-center justify-center text-center p-6 ">
            <p class="mb-2 font-bold">Your account has been set up for 2FA. To remove 2FA, click on the button below.
            </p>
            <p class="mb-4 text-base ">To reset 2FA, you must remove it first.</p>

            <button class="bg-red-600 hover:bg-red-700 mt-[2rem] text-white font-semibold py-2 px-4 rounded shadow"
              @click="confirmRemove()">
              Remove 2FA
            </button>
          </div>


          <div v-else>
            <div class="text-lg">
              <p class="font-bold mb-4 text-center text-xl">
                To enhance your account's security, enable Two-Factor Authentication (2FA).
              </p>

              <p class="mb-4 text-center text-default">
                First, install the <strong>Google Authenticator</strong> app on your phone:
                <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                  target="_blank" class="text-blue-400 underline hover:text-blue-600">Google Play</a> |
                <a href="https://apps.apple.com/app/google-authenticator/id388497605" target="_blank"
                  class="text-blue-400 underline hover:text-blue-600">App Store</a>
              </p>

              <p class="mb-6 text-center text-default">
                Once the app is installed, click the <strong>"Generate QR Code"</strong> button below
                and scan the code using the Google Authenticator app to complete setup.
              </p>

              <div class="flex flex-col lg:flex-row items-center justify-center gap-12 mt-[4rem]">
                <div class="flex flex-col items-center space-y-4">
                  <qrcode-vue v-if="otpUri.length > 0" :value="otpUri" :size="250" class="border rounded p-2" />
                    <div v-if="generateQrBtnClicked" class="mt-6 text-center">
  <p class="text-base font-bold mb-2">Can't scan the QR code?</p>

  <p class="text-base">
    Enter the following information manually in the Google Authenticator app:
  </p>

  <p class="text-base mb-3  text-left ml-[11rem]">
  <strong  class="mr-[1rem]"> Account :</strong>  {{ accountName }}
</p>

<p class="text-base mb-3 text-left ml-[11rem]">
  <strong class="mr-[1rem]">Key :</strong>
  <span class="font-mono   break-all">  {{ secret }}</span>
</p>

<p class="text-sm ">
  Make sure to choose <strong>"Time-based"</strong> when adding the key.
</p>

</div>

                  <div v-if="!generateQrBtnClicked">
                    <button class="btn btn-primary" @click="createAuth()">
                      Generate QR Code
                    </button>
                  </div>
                </div>

                <div v-if="scratchCodes.length > 0" class="max-w-sm text-center lg:text-left">
                  <p class="font-bold text-lg mb-2">Emergency Scratch Codes</p>
                  <p class="text-base  mb-3">
                    Please save these in a secure place. They can be used if you lose access to your authenticator app.
                  </p>
                  <ul class="list-disc list-inside space-y-1 text-gray-900 font-mono text-base">
                    <li v-for="(code, index) in scratchCodes" :key="index" class="text-red-600">
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
const codeGenrated = ref(false)
const loaded = ref(false)
const generateQrBtnClicked = ref(false);
const accountName = ref("")
checkExist().then(() => {
  loaded.value = true
})

async function checkExist() {
  try {
    const result = await server.execute(
      new Command(["sh", "-c", "cat ~/.google_authenticator"]),
            true
    );

    const output = result.value.getStdout().trim(); // Trim to remove newlines/spaces
    if (output.length > 0) {
      codeGenrated.value = true
      console.log(" File exists and contains content");
      return true;
    } else {
      codeGenrated.value = false

      console.warn("⚠️ File is empty or does not contain useful data");
      return false;
    }
  } catch (error) {
    codeGenrated.value = false

    console.error("❌ Failed to read .google_authenticator file:", error);
    return false;
  }
}

async function detectOS() {
  try {
    const result = await server.execute(new Command(["cat", "/etc/os-release"]), true);
    const content = new TextDecoder().decode(result.value.stdout);
    console.log("content os ", content)

    if (/^ID="?rocky"?$/m.test(content)) return "rocky";
    if (content.includes("ID=ubuntu")) return "ubuntu";
    if (content.includes("ID=fedora")) return "fedora";
    if (content.includes("ID=debian")) return "debian";

    return "unknown";
  } catch (err) {
    console.warn("⚠️ Could not detect OS:", err);
    return "unknown";
  }
}

async function createAuth() {
  try {
    const os = await detectOS();

    console.log("os ", os)

    const args = [
      "google-authenticator",
      "--time-based",
      "--disallow-reuse",
      "--rate-limit=3",
      "--rate-time=30",
      "--window-size=17",
      "--force",
    ];

    if (os === "rocky") {
      args.push("--no-confirm"); // ✅ Only add for Rocky where it's supported
    }

    console.log("args, " , args)

    const result = await server.execute(new Command(args), true);
    console.log("result", result)
    const stdout = new TextDecoder().decode(result.value.stdout);

    // Extract QR URL
    const qrMatch = stdout.match(/https:\/\/www\.google\.com\/chart\?chs=200x200[^ \n"]+/);
    const qrUrl = qrMatch?.[0] ?? null;

    if (qrUrl) {
      const chlMatch = qrUrl.match(/chl=([^&\n]+)/);
      const encodedOtpauth = chlMatch?.[1];
      if (encodedOtpauth) {
        otpUri.value = decodeURIComponent(encodedOtpauth);
        extractAccountNameFromURI(otpUri.value);
      }
    }

    // Read `.google_authenticator` file
    server
      .execute(new Command(["sh", "-c", "cat ~/.google_authenticator"]), true)
      .map((proc) => {
        const lines = proc.getStdout().split("\n");
        secret.value = lines[0]?.trim();
        scratchCodes.value.push(...lines.filter((line) => /^\d{8}$/.test(line.trim())));
      });

    generateQrBtnClicked.value = true;
  } catch (e) {
    console.error("❌ Failed to generate OTP:", e);
  }
}

// async function createAuth() {
//   try {
//     const result = await server.execute(
//       new Command([
//         "google-authenticator",
//         "--time-based",
//         "--disallow-reuse",
//         "--rate-limit=3",
//         "--rate-time=30",
//         "--window-size=17",
//         "--no-confirm",
//         "--force"
//       ]),
//       true
//     );
//     // Decode Uint8Array to string
//     const stdoutBytes = result.value.stdout;
//     const stdout = new TextDecoder().decode(stdoutBytes);
//     console.log("Decoded output:", stdout);

//     // Extract QR URL
//     const qrMatch = stdout.match(
//       /https:\/\/www\.google\.com\/chart\?chs=200x200[^ \n"]+/
//     );
//     const qrUrl = qrMatch?.[0] ?? null;

//     if (qrUrl) {
//       // Extract the otpauth URI from the 'chl' parameter
//       const chlMatch = qrUrl.match(/chl=([^&\n]+)/);
//       const encodedOtpauth = chlMatch?.[1];

//       if (encodedOtpauth) {
//         // Decode it
//         const otpauthUri = decodeURIComponent(encodedOtpauth);
//         console.log("✅ OTP Auth URI:", otpauthUri);

//         // Example: use in UI
//         otpUri.value = otpauthUri;
//         extractAccountNameFromURI(otpUri.value);
//       } else {
//         console.warn("⚠️ Couldn't find 'chl=' param in QR URL");
//       }
//     } else {
//       console.error("❌ QR URL not found in stdout");
//     }
//     server
//       .execute(  new Command(["sh", "-c", "cat ~/.google_authenticator"]), true)
//       .map((proc) => {
//         const lines = proc.getStdout().split("\n");
//         console.log("lines", lines)
//         secret.value = lines[0]?.trim(); // ✅ Save secret separately
//         scratchCodes.value.push(...lines.filter((line) => /^\d{8}$/.test(line.trim())));
//       });

//       //fetching username and hoste name from 
//     generateQrBtnClicked.value = true
//   } catch (e) {

//     console.error("Failed to generate OTP:", e);
//     return null;
//   }
// }

function extractAccountNameFromURI(uri: string) {
  const match = uri.match(/^otpauth:\/\/totp\/([^?]+)/);
  if (match && match[1]) {
    accountName.value = decodeURIComponent(match[1]);
  }
}

function confirmRemove() {
  if (confirm("Are you sure you want to remove 2FA for this account?")) {
    remove2FA();
  }
}

async function remove2FA() {

  const result = await server.execute(
new Command(["sh", "-c", "rm -f ~/.google_authenticator"]
    ),
    true
  );
  codeGenrated.value = false;
}
</script>
