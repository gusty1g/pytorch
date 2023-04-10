import warnings

from .base_scheduler import BaseScheduler

__all__ = ["LambdaSL"]

class LambdaSL(BaseScheduler):
    """Sets the sparsity level of each parameter group to the final sl
    times a given function. When last_epoch=-1, sets initial sl as zero.
    Args:
        pruner (BasePruner): Wrapped pruner.
        sl_lambda (function or list): A function which computes a multiplicative
            factor given an integer parameter epoch, or a list of such
            functions, one for each group in pruner.param_groups.
        last_epoch (int): The index of last epoch. Default: -1.
        verbose (bool): If ``True``, prints a message to stdout for
            each update. Default: ``False``.
    Example:
        >>> # Assuming pruner has two groups.
        >>> lambda1 = lambda epoch: epoch // 30
        >>> lambda2 = lambda epoch: 0.95 ** epoch
        >>> # xdoctest: +SKIP
        >>> scheduler = LambdaSL(pruner, sl_lambda=[lambda1, lambda2])
        >>> for epoch in range(100):
        >>>     train(...)
        >>>     validate(...)
        >>>     scheduler.step()
    """

    def __init__(self, pruner, sl_lambda, last_epoch=-1, verbose=False):
        self.pruner = pruner

        if not isinstance(sl_lambda, list) and not isinstance(sl_lambda, tuple):
            self.sl_lambdas = [sl_lambda] * len(pruner.groups)
        else:
            if len(sl_lambda) != len(pruner.groups):
                raise ValueError("Expected {} lr_lambdas, but got {}".format(
                    len(pruner.groups), len(sl_lambda)))
            self.sl_lambdas = list(sl_lambda)
        super().__init__(pruner, last_epoch, verbose)

    def get_sl(self):
        if not self._get_sl_called_within_step:
            warnings.warn(
                "To get the last sparsity level computed by the scheduler, "
                "please use `get_last_sl()`.")
        return [base_sl * lmbda(self.last_epoch)
                for lmbda, base_sl in zip(self.sl_lambdas, self.base_sl)]
