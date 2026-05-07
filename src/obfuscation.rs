use std::collections::BTreeMap;
use std::path::Path;

use aes_gcm::{
    Aes256Gcm, Nonce,
    aead::{Aead, KeyInit},
};
use rand::RngCore;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

const MANIFEST_KEY: [u8; 32] = [
    0x4f, 0x9c, 0x2a, 0x71, 0x8d, 0x36, 0xb5, 0xe2, 0xc8, 0x14, 0x6f, 0xa0, 0x3e, 0x59, 0xd7, 0x82,
    0x1b, 0x4d, 0x96, 0x07, 0xc3, 0x2e, 0x68, 0xfa, 0x55, 0x91, 0xb4, 0x07, 0xd2, 0x6b, 0x39, 0xae,
];

const NONCE_LEN: usize = 12;
const HASH_HEX_LEN: usize = 16;

pub const MANIFEST_FILENAME: &str = "manifest.bin";
pub const MANIFEST_VERSION: u32 = 1;

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct Manifest {
    pub version: u32,
    pub categories: BTreeMap<String, CategoryEntry>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CategoryEntry {
    pub name: String,
    pub items: BTreeMap<String, String>,
}

pub fn hash_name(name: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(name.as_bytes());
    let digest = hasher.finalize();
    hex_encode(&digest[..HASH_HEX_LEN / 2])
}

fn hex_encode(bytes: &[u8]) -> String {
    let mut out = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        out.push_str(&format!("{b:02x}"));
    }
    out
}

pub fn encrypt(plaintext: &[u8]) -> Result<Vec<u8>, String> {
    let cipher = Aes256Gcm::new_from_slice(&MANIFEST_KEY).map_err(|e| e.to_string())?;
    let mut nonce_bytes = [0u8; NONCE_LEN];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);
    let ciphertext = cipher
        .encrypt(nonce, plaintext)
        .map_err(|e| format!("encrypt failed: {e}"))?;

    let mut out = Vec::with_capacity(NONCE_LEN + ciphertext.len());
    out.extend_from_slice(&nonce_bytes);
    out.extend(ciphertext);
    Ok(out)
}

pub fn decrypt(data: &[u8]) -> Result<Vec<u8>, String> {
    if data.len() <= NONCE_LEN {
        return Err("manifest too small".to_owned());
    }

    let cipher = Aes256Gcm::new_from_slice(&MANIFEST_KEY).map_err(|e| e.to_string())?;
    let (nonce_bytes, ciphertext) = data.split_at(NONCE_LEN);
    let nonce = Nonce::from_slice(nonce_bytes);
    cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| format!("decrypt failed: {e}"))
}

pub fn load_manifest(path: &Path) -> Option<Manifest> {
    let bytes = std::fs::read(path).ok()?;
    let plaintext = decrypt(&bytes).ok()?;
    serde_json::from_slice(&plaintext).ok()
}

pub fn save_manifest(path: &Path, manifest: &Manifest) -> Result<(), String> {
    let json = serde_json::to_vec(manifest).map_err(|e| e.to_string())?;
    let encrypted = encrypt(&json)?;
    std::fs::write(path, encrypted).map_err(|e| e.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_is_deterministic() {
        assert_eq!(hash_name("奧塔"), hash_name("奧塔"));
        assert_ne!(hash_name("奧塔"), hash_name("不死鳥"));
        assert_eq!(hash_name("奧塔").len(), HASH_HEX_LEN);
    }

    #[test]
    fn encrypt_decrypt_roundtrip() {
        let plain = b"hello world payload";
        let cipher = encrypt(plain).unwrap();
        assert_ne!(cipher, plain);
        let recovered = decrypt(&cipher).unwrap();
        assert_eq!(recovered, plain);
    }

    #[test]
    fn manifest_roundtrip() {
        let mut manifest = Manifest {
            version: MANIFEST_VERSION,
            categories: BTreeMap::new(),
        };
        manifest.categories.insert(
            hash_name("BOSS"),
            CategoryEntry {
                name: "BOSS".to_owned(),
                items: BTreeMap::from([(hash_name("奧塔"), "奧塔".to_owned())]),
            },
        );

        let dir = std::env::temp_dir().join(format!(
            "lineage_obf_test_{}",
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join(MANIFEST_FILENAME);
        save_manifest(&path, &manifest).unwrap();
        let loaded = load_manifest(&path).unwrap();
        assert_eq!(loaded.version, MANIFEST_VERSION);
        assert_eq!(loaded.categories.len(), 1);

        std::fs::remove_dir_all(dir).unwrap();
    }
}
