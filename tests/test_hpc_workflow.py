#!/usr/bin/env python3
"""
Test suite for HPC workflow module.
"""
import sys
import pytest
from tools.hpc_workflow import JobScheduler, RegressionTestRunner


class TestJobSubmission:
    """Test job submission."""
    
    def test_submit_analysis_basic(self):
        """Test basic job submission."""
        scheduler = JobScheduler()
        job = scheduler.submit_analysis('test_case.dat', solver='OpenSees', num_threads=4)
        
        assert job['job_id'].startswith('JOB_')
        assert job['name'] == 'test_case.dat'
        assert job['solver'] == 'OpenSees'
        assert 'status' in job
    
    def test_submit_analysis_different_types(self):
        """Test different analysis types."""
        scheduler = JobScheduler()
        
        job1 = scheduler.submit_analysis('case1.dat', 'OpenSees')
        job2 = scheduler.submit_analysis('case2.dat', 'CalculiX')
        job3 = scheduler.submit_analysis('case3.dat', 'ETABS')
        
        assert job1['solver'] == 'OpenSees'
        assert job2['solver'] == 'CalculiX'
        assert job3['solver'] == 'ETABS'
    
    def test_job_queue_position(self):
        """Test job queue position."""
        scheduler = JobScheduler()
        
        job1 = scheduler.submit_analysis('case1.dat', 'OpenSees')
        job2 = scheduler.submit_analysis('case2.dat', 'OpenSees')
        
        # Jobs should be queued
        assert job1['queue_position'] == 1
        assert job2['queue_position'] == 2
    
    def test_submit_analysis_thread_count(self):
        """Test thread count in submission."""
        scheduler = JobScheduler()
        
        job = scheduler.submit_analysis('case.dat', 'OpenSees', num_threads=8)
        assert job['job_id']  # Just verify it returns a job


class TestBatchProcessing:
    """Test batch parallel analysis."""
    
    def test_batch_parallel_analyses_basic(self):
        """Test basic batch processing."""
        scheduler = JobScheduler()
        
        cases = ['case1.dat', 'case2.dat', 'case3.dat']
        
        batch = scheduler.batch_parallel_analyses(cases, solver='OpenSees')
        
        assert 'total_cases' in batch
        assert batch['total_cases'] == 3
        assert 'num_batches' in batch
    
    def test_batch_batching_logic(self):
        """Test batch distribution logic."""
        scheduler = JobScheduler()
        
        cases = [f'case{i}.dat' for i in range(6)]
        batch = scheduler.batch_parallel_analyses(cases, batch_size=2)
        
        assert batch['total_cases'] == 6
        assert batch['num_batches'] == 3
    
    def test_batch_single_worker(self):
        """Test batch with single worker."""
        scheduler = JobScheduler()
        
        cases = ['case1.dat', 'case2.dat']
        
        batch = scheduler.batch_parallel_analyses(cases, batch_size=1)
        assert batch['total_cases'] == 2
    
    def test_batch_large_job_count(self):
        """Test batch with many jobs."""
        scheduler = JobScheduler()
        
        cases = [f'case{i}.dat' for i in range(20)]
        batch = scheduler.batch_parallel_analyses(cases, batch_size=5)
        
        assert batch['total_cases'] == 20
        assert batch['num_batches'] == 4


class TestQueueStatus:
    """Test queue status tracking."""
    
    def test_queue_status_basic(self):
        """Test basic queue status."""
        scheduler = JobScheduler()
        
        # Submit some jobs
        scheduler.submit_analysis('case1.dat', 'OpenSees')
        scheduler.submit_analysis('case2.dat', 'OpenSees')
        
        status = scheduler.queue_status()
        
        assert 'num_workers' in status
        assert 'queued_jobs' in status
        assert 'completed_jobs' in status
    
    def test_queue_status_with_submissions(self):
        """Test queue status with multiple submissions."""
        scheduler = JobScheduler()
        
        for i in range(5):
            scheduler.submit_analysis(f'case{i}.dat', 'OpenSees')
        
        status = scheduler.queue_status()
        assert status['queued_jobs'] == 5
    
    def test_queue_utilization(self):
        """Test queue utilization metrics."""
        scheduler = JobScheduler()
        
        scheduler.submit_analysis('case1.dat', 'OpenSees')
        status = scheduler.queue_status()
        
        assert 'num_workers' in status


class TestRegressionTesting:
    """Test regression testing framework."""
    
    def test_run_benchmark_suite_basic(self):
        """Test basic benchmark suite run."""
        runner = RegressionTestRunner()
        
        benchmark_cases = ['burj_khalifa', 'shanghai_tower']
        
        results = runner.run_benchmark_suite(benchmark_cases)
        
        assert 'total_benchmarks' in results
        assert results['total_benchmarks'] == 2
        assert 'results' in results
    
    def test_benchmark_results_structure(self):
        """Test benchmark results structure."""
        runner = RegressionTestRunner()
        
        cases = ['case1']
        results = runner.run_benchmark_suite(cases)
        
        assert 'passed' in results
        assert 'failed' in results
    
    def test_multiple_benchmark_runs(self):
        """Test multiple benchmark runs."""
        runner = RegressionTestRunner()
        
        cases = ['case1', 'case2']
        
        run1 = runner.run_benchmark_suite(cases)
        run2 = runner.run_benchmark_suite(cases)
        
        # Both runs should complete
        assert run1['total_benchmarks'] == 2
        assert run2['total_benchmarks'] == 2


class TestPerformanceScaling:
    """Test performance scaling analysis."""
    
    def test_performance_scaling_basic(self):
        """Test basic performance scaling."""
        runner = RegressionTestRunner()
        
        scaling = runner.performance_scaling('OpenSees', [1, 2, 4])
        
        assert 'solver' in scaling
        assert 'scaling_data' in scaling
        assert len(scaling['scaling_data']) >= 1
    
    def test_scaling_results_metrics(self):
        """Test scaling results metrics."""
        runner = RegressionTestRunner()
        
        scaling = runner.performance_scaling('OpenSees', [1, 2, 4])
        
        for result in scaling['scaling_data']:
            assert 'num_threads' in result
            assert 'wall_time_seconds' in result
            assert 'speedup' in result
            assert 'efficiency_percent' in result
    
    def test_scaling_thread_range(self):
        """Test scaling across thread range."""
        runner = RegressionTestRunner()
        
        scaling = runner.performance_scaling('OpenSees', [1, 2, 4, 8])
        
        # Should have results for specified threads
        assert len(scaling['scaling_data']) == 4
    
    def test_speedup_calculation(self):
        """Test speedup calculation in scaling."""
        runner = RegressionTestRunner()
        
        scaling = runner.performance_scaling('OpenSees', [1, 2, 4])
        
        # Verify speedup data present
        if len(scaling['scaling_data']) > 0:
            first = scaling['scaling_data'][0]
            assert 'speedup' in first


class TestIntegration:
    """Integration tests for HPC workflow."""
    
    def test_full_hpc_workflow(self):
        """Test full HPC workflow."""
        scheduler = JobScheduler()
        runner = RegressionTestRunner()
        
        # Submit jobs
        job1 = scheduler.submit_analysis('case1.dat', 'OpenSees')
        job2 = scheduler.submit_analysis('case2.dat', 'OpenSees')
        
        # Check queue
        status = scheduler.queue_status()
        assert status['queued_jobs'] == 2
        
        # Run benchmarks
        benchmark_cases = ['case1', 'case2']
        results = runner.run_benchmark_suite(benchmark_cases)
        assert results['total_benchmarks'] == 2
    
    def test_batch_and_monitor(self):
        """Test batch submission and monitoring."""
        scheduler = JobScheduler()
        
        # Submit individual jobs (not batch planning)
        for i in range(3):
            scheduler.submit_analysis(f'case{i}.dat', 'OpenSees')
        
        # Monitor queue
        status = scheduler.queue_status()
        assert status['queued_jobs'] == 3
        
        # Also test batch planning
        cases = [f'case{i}.dat' for i in range(3)]
        batch = scheduler.batch_parallel_analyses(cases, batch_size=2)
        assert batch['total_cases'] == 3
    
    def test_scaling_analysis_workflow(self):
        """Test scaling analysis workflow."""
        runner = RegressionTestRunner()
        
        # Run scaling analysis
        scaling = runner.performance_scaling('OpenSees', [1, 2, 4])
        
        # Verify structure
        assert 'solver' in scaling
        assert len(scaling['scaling_data']) >= 2
        
        # Check efficiency trend
        efficiencies = [r['efficiency_percent'] for r in scaling['scaling_data']]
        assert len(efficiencies) >= 2


def main():
    """Run tests."""
    pytest.main([__file__, '-v'])

if __name__ == '__main__':
    main()
