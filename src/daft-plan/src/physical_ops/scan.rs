use std::sync::Arc;

use daft_scan::ScanTask;

use crate::PartitionSpec;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TabularScan {
    pub scan_tasks: Vec<Arc<ScanTask>>,
    pub partition_spec: Arc<PartitionSpec>,
}

impl TabularScan {
    pub(crate) fn new(scan_tasks: Vec<ScanTask>, partition_spec: Arc<PartitionSpec>) -> Self {
        Self {
            scan_tasks: scan_tasks.into_iter().map(Arc::new).collect(),
            partition_spec,
        }
    }
}